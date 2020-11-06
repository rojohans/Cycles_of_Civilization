import pyvista as pv
import numpy as np
import pyopencl as cl
import time

import Library.World as World



import os
#os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
#os.environ['PYOPENCL_CTX'] = '1'


world = World.SphericalWorld(nDivisions=100)

world.v[:, 0] /= world.vertexRadius
world.v[:, 1] /= world.vertexRadius
world.v[:, 2] /= world.vertexRadius

# Used for parallell assignment
faceConnectionsIndices = np.empty_like(world.faceConnections)
for iFace in range(np.size(world.faceConnections, 0)):
    for iConnection in range(3):

        connection = world.faceConnections[iFace, iConnection]
        for i in range(3):
            if iFace == world.faceConnections[connection, i]:
                faceConnectionsIndices[iFace, iConnection] = i
                break

nIterations = 1000

deltaT = np.array(0.01)
deltaT = deltaT.astype(np.float32)
flowParameter = np.array(50)
flowParameter = flowParameter.astype(np.float32)

jTarget = faceConnectionsIndices[:, 0].astype(np.int)
kTarget = faceConnectionsIndices[:, 1].astype(np.int)
lTarget = faceConnectionsIndices[:, 2].astype(np.int)

j = world.faceConnections[:, 0]
k = world.faceConnections[:, 1]
l = world.faceConnections[:, 2]
j = j.astype(np.int)
k = k.astype(np.int)
l = l.astype(np.int)

flowj = np.zeros_like(world.faceRadius, dtype=np.float32)
flowk = np.zeros_like(world.faceRadius, dtype=np.float32)
flowl = np.zeros_like(world.faceRadius, dtype=np.float32)
flowUpdatedj = np.zeros_like(world.faceRadius, dtype=np.float32)
flowUpdatedk = np.zeros_like(world.faceRadius, dtype=np.float32)
flowUpdatedl = np.zeros_like(world.faceRadius, dtype=np.float32)

height = world.faceRadius - np.min(world.faceRadius)
height = height.astype(np.float32)
heightUpdated = world.faceRadius - np.min(world.faceRadius)
heightUpdated = heightUpdated.astype(np.float32)
#heightUpdated = np.zeros_like(world.faceRadius, dtype=

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
j_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=j)
k_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=k)
l_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=l)
jTarget_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=jTarget)
kTarget_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=kTarget)
lTarget_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=lTarget)
flowj_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowj)
flowk_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowk)
flowl_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowl)
flowUpdatedj_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedj.nbytes)
flowUpdatedk_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedk.nbytes)
flowUpdatedl_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedl.nbytes)

height_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=height)
#heightUpdated_buf = cl.Buffer(ctx, mf.WRITE_ONLY, heightUpdated.nbytes)
heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE, heightUpdated.nbytes)

# int *jTarget, *int kTarget, *lTarget,

prg = cl.Program(ctx, """
    __kernel void multiply(float flowParameter, float deltaT,
    __global int *jTarget, __global int *kTarget, __global int *lTarget,
    __global int *j, __global int *k, __global int *l,
    __global float *flowj, __global float *flowk, __global float *flowl,
    __global float *flowUpdatedj, __global float *flowUpdatedk, __global float *flowUpdatedl,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *height, __global float *heightUpdated)
    {
      int i = get_global_id(0);
      
      float fj = flowj[i] + deltaT*flowParameter*(height[i]-height[j[i]]);
      if (fj<0){
      fj = 0;
      }
      
      float fk = flowk[i] + deltaT*flowParameter*(height[i]-height[k[i]]);
      if (fk<0){
      fk = 0;
      }
      
      float fl = flowl[i] + deltaT*flowParameter*(height[i]-height[l[i]]);
      if (fl<0){
      fl = 0;
      }
      
      // Maximum 50% of water can move in one time step.
      float scalingParameter = 0.5*height[i]/(deltaT*(fj + fk + fl + 0.0001));
      if (scalingParameter > 1){
      scalingParameter = 1;
      }
      fj = fj*scalingParameter;
      fk = fk*scalingParameter;
      fl = fl*scalingParameter;
      
      flowUpdatedj[i] = fj;
      flowUpdatedk[i] = fk;
      flowUpdatedl[i] = fl;
      
      switch(jTarget[i]) {
      case 0:
        flowInj[j[i]] = fj;
        break;
      case 1:
        flowInk[j[i]] = fj;
        break;
      default:
        flowInl[j[i]] = fj;
      }
      
      switch(kTarget[i]) {
      case 0:
        flowInj[k[i]] = fk;
        break;
      case 1:
        flowInk[k[i]] = fk;
        break;
      default:
        flowInl[k[i]] = fk;
      }
      
      switch(lTarget[i]) {
      case 0:
        flowInj[l[i]] = fl;
        break;
      case 1:
        flowInk[l[i]] = fl;
        break;
      default:
        flowInl[l[i]] = fl;
      }
      
      flowOut[i] = fj + fk + fl;
      
    }
    
    __kernel void UpdateWaterHeight(float deltaT,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *height, __global float *heightUpdated)
    {
      int i = get_global_id(0);
      
      heightUpdated[i] = height[i] + deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
    }
    """).build()


#heightUpdated[j[i]] = heightUpdated[j[i]] + fj;
#heightUpdated[k[i]] = heightUpdated[k[i]] + fk;
#heightUpdated[l[i]] = heightUpdated[l[i]] + fl;
#heightUpdated[i] = heightUpdated[i] - fj - fk - fl;

'''
fc = world.faceConnections
print(fc)
print(np.shape(fc))
print(type(fc))
print(fc.dtype)
f = np.zeros((np.size(fc, 0), 1))



for i in range(np.size(fc, 0)):
    #f[i] -= 3
    f[fc[i, 0:1]] += 1
    f[fc[i, 1:2]] += 1
    f[fc[i, 2:3]] += 1

print(np.min(f))
print(np.max(f))
print(np.sum(f))
#for i in range(np.size(fc, 0)):
#    print(f[i])
quit()
'''


terrainMesh = pv.PolyData(world.v, np.hstack(world.f))
plotter = pv.Plotter()
plotter.add_mesh(terrainMesh, scalars=height, smooth_shading=True, clim=[0, 5])

#plotter.enable_eye_dome_lighting()
plotter.show(auto_close=False)

ticTotalSimulation = time.time()

for i in range(nIterations):

    #height[np.random.randint(0, np.size(world.f, 0))] += 10

    heightUpdated = np.zeros_like(world.faceRadius, dtype=np.float32)
    #heightUpdated = height.copy()
    flowUpdatedj = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowUpdatedk = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowUpdatedl = np.zeros_like(world.faceRadius, dtype=np.float32)

    flowInj = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowInk = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowInl = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowOut = np.zeros_like(world.faceRadius, dtype=np.float32)

    flowj_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowj)
    flowk_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowk)
    flowl_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowl)
    flowUpdatedj_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedj.nbytes)
    flowUpdatedk_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedk.nbytes)
    flowUpdatedl_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowUpdatedl.nbytes)

    #flowInj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInj.nbytes)
    #flowInk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInk.nbytes)
    #flowInl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInl.nbytes)
    #flowOut_buf = cl.Buffer(ctx, mf.READ_WRITE, flowOut.nbytes)
    flowInj_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowInj.nbytes)
    flowInk_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowInk.nbytes)
    flowInl_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowInl.nbytes)
    flowOut_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowOut.nbytes)

    height_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=height)
    #heightUpdated_buf = cl.Buffer(ctx, mf.WRITE_ONLY, heightUpdated.nbytes)
    heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE, heightUpdated.nbytes)
    #heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=heightUpdated)

    #print(np.min(height))
    #print(np.max(height))
    #print(np.sum(height))

    #, jTarget_buf, kTarget_buf, lTarget_buf

    tic = time.time()
    prg.multiply(queue, heightUpdated.shape, None, flowParameter, deltaT, jTarget_buf, kTarget_buf, lTarget_buf,
                 j_buf, k_buf, l_buf, flowj_buf, flowk_buf, flowl_buf, flowUpdatedj_buf, flowUpdatedk_buf, flowUpdatedl_buf,
                 flowInj_buf, flowInk_buf, flowInl_buf, flowOut_buf, height_buf, heightUpdated_buf)
    toc = time.time()
    print('pyopencl simulation time : ', toc-tic)

    tic = time.time()
    prg.UpdateWaterHeight(queue, heightUpdated.shape, None, deltaT, flowInj_buf, flowInk_buf, flowInl_buf, flowOut_buf,
                          height_buf, heightUpdated_buf)
    toc = time.time()
    print('pyopencl water update time : ', toc-tic)

    #cl.enqueue_copy(queue, heightUpdated, height_buf)
    cl.enqueue_copy(queue, heightUpdated, heightUpdated_buf)
    cl.enqueue_copy(queue, flowj, flowUpdatedj_buf)
    cl.enqueue_copy(queue, flowk, flowUpdatedk_buf)
    cl.enqueue_copy(queue, flowl, flowUpdatedl_buf)

    cl.enqueue_copy(queue, flowInj, flowInj_buf)
    cl.enqueue_copy(queue, flowInk, flowInk_buf)
    cl.enqueue_copy(queue, flowInl, flowInl_buf)
    cl.enqueue_copy(queue, flowOut, flowOut_buf)

    height = heightUpdated

    '''
    tic = time.time()
    flowj *= deltaT
    flowk *= deltaT
    flowl *= deltaT
    for i in range(np.size(flowj, 0)):
        height[i] += deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i])

        #height[i] -= flowj[i] + flowk[i] + flowl[i]
        #height[j[i]] += flowj[i]
        #height[k[i]] += flowk[i]
        #height[l[i]] += flowl[i]
    print(np.sum(height))
    flowj /= deltaT
    flowk /= deltaT
    flowl /= deltaT
    toc = time.time()
    print('height update time : ', toc-tic)
    '''

    #height += heightUpdated
    #height += heightUpdated
    #height = 5*heightUpdated.copy()

    #print(np.min(height))
    #print(np.max(height))
    #print(np.sum(height))
    print('------------------------------------------------------------------')


    plotter.update_scalars(height, mesh=terrainMesh, render=False)
    plotter.render()
tocTotalSimulation = time.time()
print('Total simulation time : ', tocTotalSimulation-ticTotalSimulation)
print('Simulation done')
plotter.show(auto_close=False)

#print(np.min(a_mul_b))
#print(np.max(a_mul_b))
#print(a_mul_b)
#for a in a_mul_b:
#    print(a)


quit()


import time
import pyopencl as cl  # Import the OpenCL GPU computing API
import pyopencl.array as pycl_array  # Import PyOpenCL Array (a Numpy array plus an OpenCL buffer object)
import numpy as np  # Import Numpy number tools

context = cl.create_some_context()  # Initialize the Context
queue = cl.CommandQueue(context)  # Instantiate a Queue

aNumpy = np.random.rand(500000).astype(np.float32)
bNumpy = np.random.rand(500000).astype(np.float32)
cNumpy = np.empty_like(aNumpy)

a = pycl_array.to_device(queue, aNumpy)
b = pycl_array.to_device(queue, bNumpy)
# Create two random pyopencl arrays
c = pycl_array.empty_like(a)  # Create an empty pyopencl destination array

program = cl.Program(context, """
__kernel void sum(__global const float *a, __global const float *b, __global float *c)
{
  int i = get_global_id(0);
  c[i] = a[i] + b[i];
}""").build()  # Create the OpenCL program

def numpySum(a, b):
    return a+b

tic = time.time()
program.sum(queue, a.shape, None, a.data, b.data, c.data)  # Enqueue the program for execution and store the result in c
toc = time.time()
print('pyopencl execution time: ', toc-tic)

tic = time.time()
cNumpy = numpySum(aNumpy, bNumpy)  # Enqueue the program for execution and store the result in c
toc = time.time()
print('numpy execution time: ', toc-tic)

print("a: {}".format(a))
print("b: {}".format(b))
print("c: {}".format(c))
print(' ')
# Print all three arrays, to show sum() worked
print("a: {}".format(aNumpy))
print("b: {}".format(bNumpy))
print("c: {}".format(cNumpy))

quit()

