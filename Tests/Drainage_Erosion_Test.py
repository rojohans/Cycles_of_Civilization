import numpy as np
import noise
import matplotlib.pyplot as plt
import pyopencl
import pickle
import time
from scipy.spatial import cKDTree
import pyvista as pv
import pyopencl as cl

import Library.World as World
import Root_Directory

class OpenclKernel():
    def __init__(self, mode = 1):
        if mode == 1:
            self.Initialize1()

    def Initialize1(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
        self.kernels = cl.Program(self.ctx, """
            __kernel void Rain(float deltaT, float rainAmount,
            __global float *water)
            {
              int i = get_global_id(0);

              water[i] += deltaT * rainAmount;
            }
            
            __kernel void CalculateWaterFlow(float deltaT,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float * flowj, __global float * flowk, __global float * flowl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *suspendedSediment, __global float *water)
            {
              int i = get_global_id(0);

              float fj = 0.0;
              float fk = 0.0;
              float fl = 0.0;

              //float dHj = rock[i] + sediment[i] + suspendedSediment[i] + water[i] - rock[j[i]] - sediment[j[i]] - suspendedSediment[j[i]] - water[j[i]];
              //float dHk = rock[i] + sediment[i] + suspendedSediment[i] + water[i] - rock[k[i]] - sediment[k[i]] - suspendedSediment[k[i]] - water[k[i]];
              //float dHl = rock[i] + sediment[i] + suspendedSediment[i] + water[i] - rock[l[i]] - sediment[l[i]] - suspendedSediment[l[i]] - water[l[i]];
              float dHj = rock[i] + sediment[i] + water[i] - rock[j[i]] - sediment[j[i]] - water[j[i]];
              float dHk = rock[i] + sediment[i] + water[i] - rock[k[i]] - sediment[k[i]] - water[k[i]];
              float dHl = rock[i] + sediment[i] + water[i] - rock[l[i]] - sediment[l[i]] - water[l[i]];
              //float dHj = rock[i] + sediment[i] + suspendedSediment[i] - rock[j[i]] - sediment[j[i]] - suspendedSediment[j[i]];
              //float dHk = rock[i] + sediment[i] + suspendedSediment[i] - rock[k[i]] - sediment[k[i]] - suspendedSediment[k[i]];
              //float dHl = rock[i] + sediment[i] + suspendedSediment[i] - rock[l[i]] - sediment[l[i]] - suspendedSediment[l[i]];
              
              float flowRate = 0.1;
              if (dHj>0)
              {
                fj = flowRate*dHj;
              }
              if (dHk>0)
              {
                fk = flowRate*dHk;
              }
              if (dHl>0)
              {
                fl = flowRate*dHl;
              }

              // The flow is scaled such that no more water can leave the cell than exist in the cell.
              float scalingParameter = water[i]/(deltaT*(fj + fk + fl + 0.0001));
              if (scalingParameter > 1){
              scalingParameter = 1;
              }
              fj = fj*scalingParameter;
              fk = fk*scalingParameter;
              fl = fl*scalingParameter;

              flowj[i] = fj;
              flowk[i] = fk;
              flowl[i] = fl;

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
            __global float *water)
            {
              int i = get_global_id(0);

              water[i] += deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
            }

            __kernel void CalculateSlope( __global float * faceVertices, __global float * sedimentVertices, __global float * slope)
            {
                int i = get_global_id(0);

                int indexJ = faceVertices[0 + i*3];
                int indexK = faceVertices[1 + i*3];
                int indexL = faceVertices[2 + i*3];
                // v0
                float x0 = sedimentVertices[0 + indexK*3] - sedimentVertices[0 + indexJ*3];
                float y0 = sedimentVertices[1 + indexK*3] - sedimentVertices[1 + indexJ*3];
                float z0 = sedimentVertices[2 + indexK*3] - sedimentVertices[2 + indexJ*3];
                // v1
                float x1 = sedimentVertices[0 + indexL*3] - sedimentVertices[0 + indexJ*3];
                float y1 = sedimentVertices[1 + indexL*3] - sedimentVertices[1 + indexJ*3];
                float z1 = sedimentVertices[2 + indexL*3] - sedimentVertices[2 + indexJ*3];

                // v2 : Triangle normal vector
                float x2 = y0*z1 - y1*z0;
                float y2 = x1*z0 - x0*z1;
                float z2 = x0*y1 - x1*y0;
                float l2 = sqrt(x2*x2 + y2*y2 + z2*z2);

                // v3 : Position vector (Average of the vertices)
                float x3 = (sedimentVertices[0 + indexJ*3] + sedimentVertices[0 + indexK*3] + sedimentVertices[0 + indexL*3] )/3.0;
                float y3 = (sedimentVertices[1 + indexJ*3] + sedimentVertices[1 + indexK*3] + sedimentVertices[1 + indexL*3] )/3.0;
                float z3 = (sedimentVertices[2 + indexJ*3] + sedimentVertices[2 + indexK*3] + sedimentVertices[2 + indexL*3] )/3.0;
                float l3 = sqrt(x3*x3 + y3*y3 + z3*z3);

                float scalarProduct = x2*x3 + y2*y3 + z2*z3;

                // At cliff faces this value can exceed 1.0, which would make acos return NaN.
                float tmp = scalarProduct/(l2*l3);
                if (tmp > 1.0)
                {
                    tmp = 1.0;
                }

                slope[i] = acos(tmp);
            }
            
            __kernel void CalculateVelocity(__global float * flowInj, __global float * flowInk, __global float * flowInl,
                                            __global float * flowOut, __global float * velocity)
            {
                int i = get_global_id(0);
                velocity[i] = (velocity[i] + flowInj[i] + flowInk[i] + flowInl[i] + flowOut[i])/2.0;
            }
                
            __kernel void HydrolicErosion(float deltaT, float erosionSedimentLimit, float rockToSedimentExpansionFactor, 
            float erosionRate, global float * j, __global float * k, __global float * l, 
            global float * slope, __global float * velocity, __global float * streamPower, 
            global float * rock, __global float * sediment, __global float * suspendedSediment, __global float * water)
            {
                int i = get_global_id(0);
                
                float erosionAmount = 0.0;
                if (sediment[i]+suspendedSediment[i]<erosionSedimentLimit)
                {
                    //erosionAmount = deltaT * erosionRate * velocity[i] * velocity[i] * (erosionSedimentLimit - sediment[i]-suspendedSediment[i]);
                    //erosionAmount = deltaT * erosionRate * velocity[i] * (erosionSedimentLimit - sediment[i]-suspendedSediment[i]);
                    //erosionAmount = deltaT * erosionRate * velocity[i];
                    
                    erosionAmount = 1000*deltaT * erosionRate * velocity[i]*velocity[i]*(erosionSedimentLimit - sediment[i]-suspendedSediment[i]);
                    //erosionAmount = deltaT * erosionRate * velocity[i]*(erosionSedimentLimit - sediment[i]-suspendedSediment[i]);
                }
                //erosionAmount = 1000*deltaT * erosionRate * velocity[i]*velocity[i];
                
                rock[i] -= erosionAmount;
                sediment[i] += rockToSedimentExpansionFactor*erosionAmount;
            }
            
            __kernel void Disolve_Deposit(float deltaT, float disolveRate, float depositionRate, float carryCapacityMultiplier,
            global float * slope, __global float * velocity, __global float * streamPower, 
            global float * rock, __global float * sediment, __global float * suspendedSediment, __global float * water)
            {
                int i = get_global_id(0);
                
                float carryCapacity = carryCapacityMultiplier*velocity[i];
                if (suspendedSediment[i]>carryCapacity)
                {
                    // Deposit
                    float depositionAmount = deltaT*depositionRate*(suspendedSediment[i] - carryCapacity);
                    if (depositionAmount > suspendedSediment[i])
                    {
                        depositionAmount = suspendedSediment[i];
                    }
                    sediment[i] += depositionAmount;
                    suspendedSediment[i] -= depositionAmount;
                }else
                {
                    // Disolve
                    float disolveAmount = deltaT*disolveRate*(carryCapacity - suspendedSediment[i]);
                    if (disolveAmount > sediment[i])
                    {
                        disolveAmount = sediment[i];
                    }
                    sediment[i] -= disolveAmount;
                    suspendedSediment[i] += disolveAmount;
                }
            }
            
            __kernel void SedimentFlow(float deltaT, float flowMultiplier,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float * waterFlowj, __global float * waterFlowk, __global float * waterFlowl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *suspendedSediment, __global float *water, __global float *velocity)
            {
              int i = get_global_id(0);
              
              float fj = 0.0;
              float fk = 0.0;
              float fl = 0.0;

              float dHj = rock[i] + sediment[i] + water[i] + suspendedSediment[i] - rock[j[i]] - sediment[j[i]] - water[j[i]] - suspendedSediment[j[i]];
              float dHk = rock[i] + sediment[i] + water[i] + suspendedSediment[i] - rock[k[i]] - sediment[k[i]] - water[k[i]] - suspendedSediment[k[i]];
              float dHl = rock[i] + sediment[i] + water[i] + suspendedSediment[i] - rock[l[i]] - sediment[l[i]] - water[l[i]] - suspendedSediment[l[i]];
              //float dHj = rock[i] + sediment[i] - rock[j[i]] - sediment[j[i]];
              //float dHk = rock[i] + sediment[i] - rock[k[i]] - sediment[k[i]];
              //float dHl = rock[i] + sediment[i] - rock[l[i]] - sediment[l[i]];
              
              //float flowRate = 10*deltaT*flowMultiplier * velocity[i];
              //if (flowRate > 0.1)
              //{
              //  flowRate = 0.1;
              //}
              //flowRate = 0.1;
              
              //float flowRate = flowMultiplier;
              
              float velocityFactor = 1000*velocity[i];//water[i];
              if (velocityFactor>1.0)
              {
                velocityFactor = 1.0;
              }
              if (water[i]<=0)
              {
                velocityFactor = 1.0;
              }
              
              //float flowRate = flowMultiplier;
              float flowRate = flowMultiplier * velocityFactor;
              
              if (dHj>0)
              {
                fj = flowRate*dHj;
              }
              if (dHk>0)
              {
                fk = flowRate*dHk;
              }
              if (dHl>0)
              {
                fl = flowRate*dHl;
              }

              // The flow is scaled such that no more water can leave the cell than exist in the cell.
              float scalingParameter = 1.0*suspendedSediment[i]/(deltaT*(fj + fk + fl + 0.0001));
              if (scalingParameter > 1)
              {
                scalingParameter = 1;
              }
              fj = fj*scalingParameter;
              fk = fk*scalingParameter;
              fl = fl*scalingParameter;

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
            
            """).build()

class Erosion():
    def __init__(self,
                 rock,
                 sediment,
                 suspendedSediment,
                 water,
                 world,
                 kernel,
                 deltaT=1,
                 rainAmount=0.01,
                 erosionRate=1,
                 erosionSedimentLimit=0.1,
                 rockToSedimentExpansionFactor=1.0,
                 sedimentFlowMultiplier = 1.0,
                 disolveRate = 0.5,
                 depositionRate = 0.5,
                 carryCapacityMultiplier = 10):
        self.world = world
        self.kernel = kernel

        self.rockHeight = rock
        self.sedimentHeight = sediment
        self.suspendedSedimentHeight = suspendedSediment
        self.waterHeight = water

        self.deltaT = np.array(deltaT).astype(np.float32)
        self.rainAmount = np.array(rainAmount).astype(np.float32)



        self.erosionRate = np.array(erosionRate).astype(np.float32)
        self.erosionSedimentLimit = np.array(erosionSedimentLimit).astype(np.float32)
        self.rockToSedimentExpansionFactor = np.array(rockToSedimentExpansionFactor).astype(np.float32)

        self.sedimentFlowMultiplier = np.array(sedimentFlowMultiplier).astype(np.float32)

        self.disolveRate = np.array(disolveRate).astype(np.float32)
        self.depositionRate = np.array(depositionRate).astype(np.float32)
        self.carryCapacityMultiplier = np.array(carryCapacityMultiplier).astype(np.float32)

        self.faceCoordinatesNormalized = world.faceCoordinates.copy()
        self.faceCoordinatesNormalized[:, 0] /= world.faceRadius
        self.faceCoordinatesNormalized[:, 1] /= world.faceRadius
        self.faceCoordinatesNormalized[:, 2] /= world.faceRadius
        # Used for parallell assignment
        faceConnectionsIndices = np.empty_like(world.faceConnections)
        for iFace in range(np.size(world.faceConnections, 0)):
            for iConnection in range(3):
                connection = world.faceConnections[iFace, iConnection]
                for i in range(3):
                    if iFace == world.faceConnections[connection, i]:
                        faceConnectionsIndices[iFace, iConnection] = i
                        break


        kdTree = cKDTree(world.unscaledFaceCoordinates)
        rTypical, i = kdTree.query(world.unscaledVertices[0, :])
        rQuery, self.facesConnectingToVertex = kdTree.query(world.unscaledVertices[:, :], k=6)
        self.facesConnectingToVertex = np.array(self.facesConnectingToVertex)
        self.facesConnectingToVertex.astype(np.float32)
        self.facesConnectingToVertex_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.facesConnectingToVertex)

        self.faceVertices = world.f[:, 1:]
        self.faceVertices_buf = cl.Buffer(kernel.ctx,self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.faceVertices.astype(np.float32))

        self.rockVertices = world.unscaledVertices.copy().astype(np.float32)
        self.sedimentVertices = world.unscaledVertices.copy().astype(np.float32)
        self.waterVertices = world.unscaledVertices.copy().astype(np.float32)

        self.unscaledVertices_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,hostbuf=world.unscaledVertices.astype(np.float32))
        self.rockVertices_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.rockVertices)
        self.sedimentVertices_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.sedimentVertices)
        self.waterVertices_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.waterVertices)
        self.landVertices_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,hostbuf=world.unscaledVertices.astype(np.float32))


        jTarget = faceConnectionsIndices[:, 0].astype(np.int)
        kTarget = faceConnectionsIndices[:, 1].astype(np.int)
        lTarget = faceConnectionsIndices[:, 2].astype(np.int)

        j = world.faceConnections[:, 0]
        k = world.faceConnections[:, 1]
        l = world.faceConnections[:, 2]
        j = j.astype(np.int)
        k = k.astype(np.int)
        l = l.astype(np.int)

        self.velocity = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.slope = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.streamPower = np.zeros_like(world.faceRadius, dtype=np.float32)

        self.waterFlowj = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.waterFlowk = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.waterFlowl = np.zeros_like(world.faceRadius, dtype=np.float32)



        self.j_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=j)
        self.k_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=k)
        self.l_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=l)
        self.jTarget_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=jTarget)
        self.kTarget_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=kTarget)
        self.lTarget_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=lTarget)
        self.waterFlowj_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowj)
        self.waterFlowk_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowk)
        self.waterFlowl_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowl)
        #self.waterFlowUpdatedj_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)
        #self.waterFlowUpdatedk_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)
        #self.waterFlowUpdatedl_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)

        self.rockHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.rockHeight)
        self.waterHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterHeight)
        self.sedimentHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.sedimentHeight)
        self.suspendedSedimentHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,hostbuf=self.suspendedSedimentHeight)
        #self.heightUpdated_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE, heightUpdated.nbytes)
        #-------------------------------------------------------------------------------------------------------------




        #self.heightUpdated = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        #self.waterFlowUpdatedj = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        #self.waterFlowUpdatedk = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        #self.waterFlowUpdatedl = np.zeros_like(self.world.faceRadius, dtype=np.float32)

        self.waterFlowInj = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowInk = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowInl = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowOut = np.zeros_like(self.world.faceRadius, dtype=np.float32)

        self.waterFlowInj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInj.nbytes)
        self.waterFlowInk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInk.nbytes)
        self.waterFlowInl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInl.nbytes)
        self.waterFlowOut_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.WRITE_ONLY, self.waterFlowOut.nbytes)
        self.sedimentFlowInj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInj.nbytes)
        self.sedimentFlowInk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInk.nbytes)
        self.sedimentFlowInl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInl.nbytes)
        self.sedimentFlowOut_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.WRITE_ONLY, self.waterFlowOut.nbytes)
        #self.sedimentFlowInj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInj.nbytes)
        #self.sedimentFlowInk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInk.nbytes)
        #self.sedimentFlowInl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInl.nbytes)
        #self.sedimentFlowOut_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.WRITE_ONLY, self.waterFlowOut.nbytes)


        self.velocity_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.velocity.nbytes)
        self.slope_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.slope.nbytes)
        self.streamPower_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.slope.nbytes)

    def Run(self, nIterations):
        nIterations = nIterations

        for i in range(nIterations):
            #rainAmount = self.rainAmount
            #self.waterHeight[:, 0] += self.deltaT * rainAmount

            self.rockHeight_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE | self.kernel.mf.COPY_HOST_PTR,
                                            hostbuf=self.rockHeight)
            self.terrainHeight_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,
                                               hostbuf=self.rockHeight)
            self.waterHeight_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,
                                             hostbuf=self.waterHeight)

            #self.waterFlowj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowj)
            #self.waterFlowk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowk)
            #self.waterFlowl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowl)

            self.kernel.kernels.Rain(self.kernel.queue, self.waterHeight.shape, None, self.deltaT, self.rainAmount, self.waterHeight_buf)

            self.kernel.kernels.CalculateWaterFlow(self.kernel.queue, self.waterHeight.shape, None, self.deltaT,
                                                   self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                                   self.waterFlowj_buf, self.waterFlowk_buf, self.waterFlowl_buf,
                                                   self.waterFlowInj_buf, self.waterFlowInk_buf, self.waterFlowInl_buf, self.waterFlowOut_buf,
                                                   self.rockHeight_buf, self.sedimentHeight_buf, self.suspendedSedimentHeight_buf, self.waterHeight_buf)
            self.kernel.kernels.UpdateWaterHeight(self.kernel.queue, self.waterHeight.shape, None, self.deltaT,
                                                  self.waterFlowInj_buf, self.waterFlowInk_buf,
                                                  self.waterFlowInl_buf, self.waterFlowOut_buf,
                                                  self.waterHeight_buf)

            #self.kernel.kernels.CalculateSlope(self.kernel.queue, self.waterHeight.shape, None, self.faceVertices_buf, self.landVertices_buf, self.slope_buf)
            self.kernel.kernels.CalculateVelocity(self.kernel.queue, self.waterHeight.shape, None,
                                                  self.waterFlowInj_buf, self.waterFlowInk_buf,
                                                  self.waterFlowInl_buf, self.waterFlowOut_buf, self.velocity_buf)

            self.kernel.kernels.HydrolicErosion(self.kernel.queue, self.waterHeight.shape, None, self.deltaT,
                                                self.erosionSedimentLimit,
                                                self.rockToSedimentExpansionFactor,
                                                self.erosionRate,
                                                self.j_buf, self.k_buf, self.l_buf,
                                                self.slope_buf, self.velocity_buf, self.streamPower_buf,
                                                self.rockHeight_buf, self.sedimentHeight_buf, self.suspendedSedimentHeight_buf, self.waterHeight_buf)

            self.kernel.kernels.Disolve_Deposit(self.kernel.queue, self.waterHeight.shape, None, self.deltaT, self.disolveRate, self.depositionRate, self.carryCapacityMultiplier,
                                                self.slope_buf, self.velocity_buf, self.streamPower_buf,
                                                self.rockHeight_buf, self.sedimentHeight_buf, self.suspendedSedimentHeight_buf, self.waterHeight_buf)
            for iSedimentFlow in range(5):
                self.kernel.kernels.SedimentFlow(self.kernel.queue, self.waterHeight.shape, None, self.deltaT, self.sedimentFlowMultiplier,
                                                 self.jTarget_buf, self.kTarget_buf, self.lTarget_buf,
                                                 self.j_buf, self.k_buf, self.l_buf,
                                                 self.waterFlowj_buf, self.waterFlowk_buf, self.waterFlowl_buf,
                                                 self.sedimentFlowInj_buf, self.sedimentFlowInk_buf, self.sedimentFlowInl_buf,
                                                 self.sedimentFlowOut_buf,
                                                 self.rockHeight_buf, self.sedimentHeight_buf, self.suspendedSedimentHeight_buf, self.waterHeight_buf, self.velocity_buf)
                self.kernel.kernels.UpdateWaterHeight(self.kernel.queue, self.waterHeight.shape, None, self.deltaT,
                                                      self.sedimentFlowInj_buf, self.sedimentFlowInk_buf,
                                                      self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                                      self.suspendedSedimentHeight_buf)
            #self.kernel.kernels.UpdateVertices(self.kernel.queue, self.facesConnectingToVertex[:, 0].shape, None,
            #                                   self.nVertices, self.minRadius,
            #                                   self.facesConnectingToVertex_buf, self.unscaledVertices_buf,
            #                                   self.landVertices_buf, self.waterVertices_buf,
            #                                   self.terrainHeight_buf, self.sedimentHeight_buf, self.waterHeight_buf)


            '''
            self.kernel.kernels.CalculateWaterFlow(self.kernel.queue, self.heightUpdated.shape, None, self.flowParameter, self.deltaT, self.frictionParameter,
                                               self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                               self.waterFlowj_buf, self.waterFlowk_buf, self.qwaterFlowl_buf, self.waterFlowUpdatedj_buf,
                                               self.waterFlowUpdatedk_buf, self.waterFlowUpdatedl_buf,
                                               self.waterFlowInj_buf, self.waterFlowInk_buf, self.waterFlowInl_buf, self.waterFlowOut_buf,
                                               self.terrainHeight_buf, self.sedimentHeight_buf,
                                               self.waterHeight_buf)

            self.kernel.kernels.UpdateWaterHeight(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.waterFlowInj_buf, self.waterFlowInk_buf,
                                              self.waterFlowInl_buf, self.waterFlowOut_buf,
                                              self.waterHeight_buf, self.heightUpdated_buf)

            self.kernel.kernels.CalculateSlope(self.kernel.queue, self.heightUpdated.shape, None, self.faceVertices_buf, self.landVertices_buf, self.slope_buf)

            self.kernel.kernels.CalculateVelocity(self.kernel.queue, self.heightUpdated.shape, None, self.sqrt3_2, self.waterFlowInj_buf, self.waterFlowInk_buf,
                                              self.waterFlowInl_buf, self.waterFlowUpdatedj_buf, self.waterFlowUpdatedk_buf,
                                              self.waterFlowUpdatedl_buf, self.velocity_buf, self.waterHeight_buf, self.heightUpdated_buf)

            self.kernel.kernels.CalculateStreamPower(self.kernel.queue, self.heightUpdated.shape, None, self.streamPowerParameter, self.waterHeight_buf,
                                                 self.slope_buf, self.velocity_buf, self.streamPower_buf)

            self.kernel.kernels.SedimentFlow(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.sedimentFlowParameter,
                                         self.sedimentResistivity, self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                         self.waterFlowUpdatedj_buf, self.waterFlowUpdatedk_buf, self.waterFlowUpdatedl_buf,
                                         self.sedimentFlowInj_buf, self.sedimentFlowInk_buf, self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                         self.terrainHeight_buf, self.sedimentHeight_buf, self.slope_buf, self.streamPower_buf)
            self.kernel.kernels.SedimentSlippageUpdate(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT,
                                                   self.sedimentFlowInj_buf, self.sedimentFlowInk_buf, self.sedimentFlowInl_buf,
                                                   self.sedimentFlowOut_buf,
                                                   self.sedimentHeight_buf)

            self.kernel.kernels.HydrolicErosion(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.thermalErosionSedimentLimit,
                                            self.rockToSedimentExpansionFactor, self.minErosionRate, self.erosionRate, self.rockResistivity,
                                            self.j_buf, self.k_buf, self.l_buf,
                                            self.slope_buf, self.velocity_buf, self.streamPower_buf, self.terrainHeight_buf, self.sedimentHeight_buf,
                                            self.waterHeight_buf)

            self.kernel.kernels.ThermalErosion(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.thermalErosionRate,
                                           self.thermalErosionSedimentLimit, self.rockToSedimentExpansionFactor, self.talusAngle,
                                           self.terrainHeight_buf, self.sedimentHeight_buf, self.waterHeight_buf, self.slope_buf, self.rockResistivity)

            self.kernel.kernels.SedimentSlippageCalculation(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.slippageParameter,
                                                        self.talusAngle, self.triangleLength, self.minRadius,
                                                        self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                                        self.sedimentFlowInj_buf, self.sedimentFlowInk_buf, self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                                        self.terrainHeight_buf, self.sedimentHeight_buf, self.slope_buf)
            self.kernel.kernels.SedimentSlippageUpdate(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.sedimentFlowInj_buf,
                                                   self.sedimentFlowInk_buf, self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                                   self.sedimentHeight_buf)

            self.kernel.kernels.UpdateVertices(self.kernel.queue, self.facesConnectingToVertex[:, 0].shape, None, self.nVertices, self.minRadius,
                                               self.facesConnectingToVertex_buf, self.unscaledVertices_buf,
                                               self.landVertices_buf, self.waterVertices_buf,
                                               self.terrainHeight_buf, self.sedimentHeight_buf, self.waterHeight_buf)
            self.kernel.kernels.CalculateSlope(self.kernel.queue, self.heightUpdated.shape, None, self.faceVertices_buf,
                                               self.waterVertices_buf, self.waterSlope_buf)
            

            cl.enqueue_copy(self.kernel.queue, self.velocity, self.velocity_buf)
            cl.enqueue_copy(self.kernel.queue, self.slope, self.slope_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterSlope, self.waterSlope_buf)

            cl.enqueue_copy(self.kernel.queue, self.rockHeight, self.terrainHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.sedimentHeight, self.sedimentHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterHeight, self.heightUpdated_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowj, self.waterFlowUpdatedj_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowk, self.waterFlowUpdatedk_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowl, self.waterFlowUpdatedl_buf)

            cl.enqueue_copy(self.kernel.queue, self.streamPower, self.streamPower_buf)

            cl.enqueue_copy(self.kernel.queue, self.sedimentVertices, self.landVertices_buf)
            '''
            cl.enqueue_copy(self.kernel.queue, self.velocity, self.velocity_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowOut, self.waterFlowOut_buf)

            cl.enqueue_copy(self.kernel.queue, self.rockHeight, self.rockHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.sedimentHeight, self.sedimentHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.suspendedSedimentHeight, self.suspendedSedimentHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterHeight, self.waterHeight_buf)

            # Evaporation
            #self.waterHeight *= (1 - self.evaporationRate * self.deltaT)

class Visualizer():
    def __init__(self, world, rockHeight, sedimentHeight, suspendedSedimentHeight, waterHeight, scalars = None, scalarRange = [0, 1]):
        # Sets up lists needed to update the triangle vertices.
        kdTree = cKDTree(world.unscaledFaceCoordinates)
        rTypical, i = kdTree.query(world.unscaledVertices[0, :])
        rQuery, queryResult = kdTree.query(world.unscaledVertices[:, :], k=6)
        self.queryResult = np.array(queryResult)

        self.world = world
        # Sets up animation
        self.vertices = self.world.unscaledVertices.copy()

        rRock = rockHeight[queryResult]
        rSediment = sedimentHeight[queryResult]
        rSuspendedSediment = suspendedSedimentHeight[queryResult]
        rWater = waterHeight[queryResult]
        r = self.world.minRadius + np.sum(rRock[:, :, 0] + rSediment[:, :, 0] + rSuspendedSediment[:, :, 0] + rWater[:, :, 0], axis=1) / 6
        self.vertices[:, 0] = r * self.world.unscaledVertices[:, 0]
        self.vertices[:, 1] = r * self.world.unscaledVertices[:, 1]
        self.vertices[:, 2] = r * self.world.unscaledVertices[:, 2]

        self.mesh = pv.PolyData(self.vertices, np.hstack(self.world.f))

        self.plotter = pv.Plotter()
        if type(scalars) == 'NoneType':
            self.plotter.add_mesh(self.mesh, smooth_shading=False, color=(0.2, 0.15, 0.15, 1))
        else:
            self.plotter.add_mesh(self.mesh, scalars=scalars, smooth_shading=False, color=(0.2, 0.15, 0.15, 1), clim=scalarRange, cmap='terrain')


        #self.plotter.enable_eye_dome_lighting()
        self.plotter.show(auto_close=False)

    def Update(self, rockHeight, sedimentHeight, suspendedSedimentHeight, waterHeight, erosion, scalars = None):

        rRock = rockHeight[self.queryResult]
        rSediment = sedimentHeight[self.queryResult]
        rSuspendedSediment = suspendedSedimentHeight[self.queryResult]
        rWater = waterHeight[self.queryResult]
        r = self.world.minRadius + np.sum(rRock[:, :, 0] + rSediment[:, :, 0] + rSuspendedSediment[:, :, 0] + rWater[:, :, 0], axis=1) / 6
        self.vertices[:, 0] = r * self.world.unscaledVertices[:, 0]
        self.vertices[:, 1] = r * self.world.unscaledVertices[:, 1]
        self.vertices[:, 2] = r * self.world.unscaledVertices[:, 2]

        self.plotter.update_coordinates(points=self.vertices, mesh=self.mesh, render=False)

        if type(scalars) != 'NoneType':
            self.plotter.update_scalars(scalars, mesh=self.mesh, render=False)

        self.mesh.compute_normals(point_normals=True, inplace=True)
        self.plotter.render()

def InitializeEarth(world, seaLevel = 1):
    faceCoordinatesNormalized = world.faceCoordinates.copy()
    faceCoordinatesNormalized[:, 0] /= world.faceRadius
    faceCoordinatesNormalized[:, 1] /= world.faceRadius
    faceCoordinatesNormalized[:, 2] /= world.faceRadius
    cutOffHeight = 6
    #rockHeight = 8 * world.WarpedPerlinNoise(faceCoordinatesNormalized,
    #                                         xWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         yWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         zWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         octaves=15, persistence=0.6) + \
    #             6 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.5)

    #rockHeight = 1 * world.WarpedPerlinNoise(faceCoordinatesNormalized,
    #                                         xWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         yWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         zWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
    #                                         octaves=15, persistence=0.6, scale=0.5)

    #rockHeight = 2/(1+rockHeight)-1

    #rockHeight = 4 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6, scale=0.5)**2
    #rockHeight *= world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3, scale=0.5)

    #rockHeight = 1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.5, scale=0.5)

    '''
    weight = 1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.1, scale=0.5)
    #rockHeight = 0.5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3, scale=0.002) + \
    #             0.5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6, scale=0.5)
    rockHeight = weight * np.sqrt(world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.2, scale=0.002)) + \
                 (1-weight) * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6, scale=0.5)
    '''
    rockHeight = 2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.4, scale=0.5) + \
                 0.2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.8, scale=0.5)
    #rockHeight = np.sqrt((1 - 2 * np.abs(world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3) - 0.5))) ** 1 + \
    #             0.1*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.8)

    #rockHeight = 0.2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3, scale=0.5) + \
    #             0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.5, scale=0.5)
    rockHeight *= 5


    peaks = world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6, scale=0.5)
    peaks -= 0.7
    peaks[peaks<0] = 0
    peaks /= np.max(peaks)
    peaks = np.sqrt(peaks)
    peaks *= 1
    #rockHeight += peaks
    '''
    continentPerlin = 1 * world.WarpedPerlinNoise(faceCoordinatesNormalized,
                                             xWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             yWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             zWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             octaves=15, persistence=0.1)
    continentPerlin = np.sin(continentPerlin*np.pi/2)**2
    continentPerlinTmp = continentPerlin.copy()
    continentPerlinTmp -= 0.5
    continentPerlin[continentPerlinTmp<0] = 0.5
    continentPerlin[continentPerlinTmp>0] = 0
    continentPerlin *= 1
    '''
    rockHeight *= 3

    #rockHeight[rockHeight>seaLevel] = seaLevel
    #landmassNoise = 10*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.7)**3
    #rockHeight[rockHeight == seaLevel] += landmassNoise[rockHeight == seaLevel]

    #rockHeight += continentPerlin

    sedimentHeight = 0*rockHeight.copy()
    suspendedSedimentHeight = 0 * rockHeight.copy()
    waterHeight = 0*rockHeight.copy()
    waterHeight[rockHeight<seaLevel] = seaLevel - rockHeight[rockHeight<seaLevel]
    rockHeight = rockHeight.astype(np.float32)
    sedimentHeight = sedimentHeight.astype(np.float32)
    suspendedSedimentHeight = suspendedSedimentHeight.astype(np.float32)
    waterHeight = waterHeight.astype(np.float32)
    return [rockHeight, sedimentHeight, suspendedSedimentHeight, waterHeight]

def Main():
    nDivisions = 100
    useScalars = True
    seaLevel = 7

    fileToOpen = 'world_template_' + str(nDivisions) + '.pkl'
    try:
        world = pickle.load(open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "rb"))
    except:
        world = World.SphericalWorld(nDivisions=nDivisions)
        pickle.dump(world, open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "wb"))
    print('Number of triangles: ', np.size(world.f, 0))

    # Used for parallell assignment
    faceConnectionsIndices = np.empty_like(world.faceConnections)
    for iFace in range(np.size(world.faceConnections, 0)):
        for iConnection in range(3):

            connection = world.faceConnections[iFace, iConnection]
            for i in range(3):
                if iFace == world.faceConnections[connection, i]:
                    faceConnectionsIndices[iFace, iConnection] = i
                    break
    faceCoordinatesNormalized = world.faceCoordinates.copy()
    faceCoordinatesNormalized[:, 0] /= world.faceRadius
    faceCoordinatesNormalized[:, 1] /= world.faceRadius
    faceCoordinatesNormalized[:, 2] /= world.faceRadius

    print(world.minRadius)

    kernels = OpenclKernel(mode=1)
    print('kernels initialized')


    [rockHeight, sedimentHeight, suspendedSedimentHeight, waterHeight] = InitializeEarth(world=world, seaLevel=seaLevel)
    print('Heights initialized')

    initialRockHeight = rockHeight.copy()
    #rockHeight *= 0.1
    #waterHeight *= 0.1

    if useScalars:
        #visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[0, 2])
        #visualizer = Visualizer(world=world, rockHeight=rockHeight,sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[0, 0.005])
        #visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[0, 2])
        #visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,scalars=waterHeight[:, 0], scalarRange=[0, 2])
        visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[seaLevel, np.max(rockHeight)])
    else:
        visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight)
    print('Visualizer initialized')

    erosion = Erosion(rock=rockHeight,
                      sediment=sedimentHeight,
                      suspendedSediment=suspendedSedimentHeight,
                      water=waterHeight,
                      world=world,
                      kernel=kernels,
                      deltaT=1,
                      rainAmount=0.00001,
                      erosionRate = 100,
                      erosionSedimentLimit = 0.1,
                      rockToSedimentExpansionFactor = 1.0,
                      sedimentFlowMultiplier = 0.2,
                      carryCapacityMultiplier=10,#10
                      depositionRate=1,
                      disolveRate=0.05)#0.05

    ticTotalSimulation = time.time()
    for i in range(2000):
        if i == 2000 and True:
            erosion.rainAmount = np.array(0).astype(np.float32)
            print('--- RAIN STOPPED ---')
        erosion.Run(nIterations=1)
        if i%10==0 and False:
            if useScalars:
                visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight,erosion=erosion, scalars=waterHeight[:, 0])
                #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=erosion.velocity)
                #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=suspendedSedimentHeight[:, 0])
                #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=suspendedSedimentHeight[:, 0])
                #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=rockHeight[:, 0] + sedimentHeight[:, 0] + suspendedSedimentHeight[:, 0] + waterHeight[:, 0])
            else:
                visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight, erosion=erosion)
    tocTotalSimulation = time.time()
    print('TOTAL SIMULATION TIME : ', tocTotalSimulation-ticTotalSimulation)
    if useScalars:
        #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight,erosion=erosion, scalars=waterHeight[:, 0])
        #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight,erosion=erosion, scalars=erosion.velocity)
        #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=sedimentHeight[:, 0])
        #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight, erosion=erosion,scalars=suspendedSedimentHeight[:, 0])
        visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=rockHeight[:, 0] + sedimentHeight[:, 0] + suspendedSedimentHeight[:, 0] + waterHeight[:, 0])
    else:
        visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,
                          erosion=erosion)
    print('Initial landmass : ', np.sum(initialRockHeight))
    print('Rock : ', np.sum(rockHeight))
    print('Sediment : ', np.sum(sedimentHeight))
    print('suspendedSediment : ', np.sum(suspendedSedimentHeight))
    print('Current landmass : ', np.sum(rockHeight + sedimentHeight + suspendedSedimentHeight))

    '''
    # Save topography to file.
    world.v = visualizer.rockVertices
    world.vertexRadius = world.CalculateVertexRadius(world.v)
    world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
    pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldRock_15.pkl', "wb"))

    world.v = visualizer.waterVertices
    world.vertexRadius = world.CalculateVertexRadius(world.v)
    world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
    pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldWater_15.pkl', "wb"))

    
    pickle.dump(SaveClass(world=world, rock=visualizer.rockVertices, sediment=visualizer.sedimentVertices, water=visualizer.waterVertices),
                open(Root_Directory.Path() + '/Data/tmp_Data/erodedWorld_06.pkl', "wb"))
    '''
    visualizer.plotter.render()
    visualizer.plotter.show(auto_close=False)

def MainGraph():
    nDivisions = 100
    useScalars = True
    seaLevel = 0

    fileToOpen = 'world_template_' + str(nDivisions) + '.pkl'
    try:
        world = pickle.load(open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "rb"))
    except:
        world = World.SphericalWorld(nDivisions=nDivisions)
        pickle.dump(world, open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "wb"))
    print('Number of triangles: ', np.size(world.f, 0))

    # Used for parallell assignment
    faceConnectionsIndices = np.empty_like(world.faceConnections)
    for iFace in range(np.size(world.faceConnections, 0)):
        for iConnection in range(3):

            connection = world.faceConnections[iFace, iConnection]
            for i in range(3):
                if iFace == world.faceConnections[connection, i]:
                    faceConnectionsIndices[iFace, iConnection] = i
                    break
    faceCoordinatesNormalized = world.faceCoordinates.copy()
    faceCoordinatesNormalized[:, 0] /= world.faceRadius
    faceCoordinatesNormalized[:, 1] /= world.faceRadius
    faceCoordinatesNormalized[:, 2] /= world.faceRadius

    print(world.minRadius)

    #kernels = OpenclKernel(mode=1)
    #print('kernels initialized')

    [rockHeight, sedimentHeight, suspendedSedimentHeight, waterHeight] = InitializeEarth(world=world, seaLevel=seaLevel)
    print('Heights initialized')
    tic = time.time()
    flowFrom = {}
    flowTo = [None for iTile in range(np.size(world.f, 0))]
    flow = [0 for iTile in range(np.size(world.f, 0))]
    for iTile in range(np.size(world.f, 0)):
        flowFrom[iTile] = []

    for iTile in range(np.size(world.f, 0)):
        j, k, l = world.faceConnections[iTile]

        dHj = rockHeight[iTile] - rockHeight[j]
        dHk = rockHeight[iTile] - rockHeight[k]
        dHl = rockHeight[iTile] - rockHeight[l]

        if dHj>0 or dHk>0 or dHl>0:
            maxIndex = 0
            dHMax = 0
            if dHj > dHMax:
                dHMax = dHj
                maxIndex = j
            if dHk > dHMax:
                dHMax = dHk
                maxIndex = k
            if dHl > dHMax:
                dHMax = dHl
                maxIndex = l
            flowFrom[maxIndex].append(iTile)
            flowTo[iTile] = maxIndex
    for startTile in flowTo:
        tile = startTile
        while tile != None:
            flow[tile] += 1
            tile = flowTo[tile]

    toc = time.time()
    print('Drainage graph creation time : ', toc-tic)

    scalars = flow
    scalarRange = [0, 100]
    if useScalars:
        #visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,scalars=waterHeight[:, 0], scalarRange=[0, 1])
        # visualizer = Visualizer(world=world, rockHeight=rockHeight,sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[0, 0.005])
        # visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[0, 2])
        # visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,scalars=waterHeight[:, 0], scalarRange=[0, 2])
        #visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, scalars=waterHeight[:, 0], scalarRange=[seaLevel, np.max(rockHeight)])

        visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,scalars=scalars, scalarRange=scalarRange)
    else:
        visualizer = Visualizer(world=world, rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight)
    print('Visualizer initialized')

    quit()


    '''
    erosion = Erosion(rock=rockHeight,
                      sediment=sedimentHeight,
                      suspendedSediment=suspendedSedimentHeight,
                      water=waterHeight,
                      world=world,
                      kernel=kernels,
                      deltaT=1,
                      rainAmount=0.00001,
                      erosionRate=10,
                      erosionSedimentLimit=0.1,
                      rockToSedimentExpansionFactor=1.0,
                      sedimentFlowMultiplier=0.1,
                      carryCapacityMultiplier=100,
                      depositionRate=0.5,
                      disolveRate=0.5)

    ticTotalSimulation = time.time()
    for i in range(2000):
        if i == 2000 and True:
            erosion.rainAmount = np.array(0).astype(np.float32)
            print('--- RAIN STOPPED ---')
        erosion.Run(nIterations=1)
        if i % 10 == 0 and False:
            if useScalars:
                #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=waterHeight[:, 0])
                # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=erosion.velocity)
                # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=suspendedSedimentHeight[:, 0])
                # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=suspendedSedimentHeight[:, 0])
                visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=erosion, scalars=rockHeight[:, 0] + sedimentHeight[:, 0] + suspendedSedimentHeight[:, 0] + waterHeight[:, 0])
            else:
                visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,
                                  suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,
                                  erosion=erosion)
    tocTotalSimulation = time.time()
    print('TOTAL SIMULATION TIME : ', tocTotalSimulation - ticTotalSimulation)
    '''
    if useScalars:
        #visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight, erosion=erosion,scalars=waterHeight[:, 0])
        # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight,erosion=erosion, scalars=erosion.velocity)
        # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight,waterHeight=waterHeight, erosion=erosion, scalars=sedimentHeight[:, 0])
        # visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight,suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight, erosion=erosion,scalars=suspendedSedimentHeight[:, 0])
        visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight,erosion=None, scalars=rockHeight[:, 0] + sedimentHeight[:, 0] + suspendedSedimentHeight[:, 0] + waterHeight[:, 0])
    else:
        visualizer.Update(rockHeight=rockHeight, sedimentHeight=sedimentHeight, suspendedSedimentHeight=suspendedSedimentHeight, waterHeight=waterHeight, erosion=None)
    '''
    # Save topography to file.
    world.v = visualizer.rockVertices
    world.vertexRadius = world.CalculateVertexRadius(world.v)
    world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
    pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldRock_15.pkl', "wb"))

    world.v = visualizer.waterVertices
    world.vertexRadius = world.CalculateVertexRadius(world.v)
    world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
    pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldWater_15.pkl', "wb"))


    pickle.dump(SaveClass(world=world, rock=visualizer.rockVertices, sediment=visualizer.sedimentVertices, water=visualizer.waterVertices),
                open(Root_Directory.Path() + '/Data/tmp_Data/erodedWorld_06.pkl', "wb"))
    '''
    visualizer.plotter.render()
    visualizer.plotter.show(auto_close=False)

#MainGraph()
Main()