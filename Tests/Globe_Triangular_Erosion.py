import pyvista as pv
import numpy as np
import pyopencl as cl
import time
import pickle
from scipy.spatial import cKDTree

import Library.World as World
import Root_Directory

#waterHeight = world.faceRadius - np.min(world.faceRadius)
#waterHeight = waterHeight.astype(np.float32)
waterHeight = np.zeros_like(world.faceRadius, dtype=np.float32)
heightUpdated = world.faceRadius - np.min(world.faceRadius)
heightUpdated = heightUpdated.astype(np.float32)
#heightUpdated = np.zeros_like(world.faceRadius, dtype=

velocity = np.zeros_like(world.faceRadius, dtype=np.float32)
slope = np.zeros_like(world.faceRadius, dtype=np.float32)

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

terrainHeight_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=terrainHeight)
waterHeight_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=waterHeight)
#heightUpdated_buf = cl.Buffer(ctx, mf.WRITE_ONLY, heightUpdated.nbytes)
heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE, heightUpdated.nbytes)

suspendedSediment = np.zeros_like(world.faceRadius, dtype=np.float32)
suspendedSediment_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=suspendedSediment)

# int *jTarget, *int kTarget, *lTarget,

prg = cl.Program(ctx, """
    __kernel void CalculateWaterFlow(float flowParameter, float deltaT, float frictionParameter,
    __global int *jTarget, __global int *kTarget, __global int *lTarget,
    __global int *j, __global int *k, __global int *l,
    __global float *flowj, __global float *flowk, __global float *flowl,
    __global float * flowOutj, __global float * flowOutk, __global float * flowOutl,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *terrain, __global float *suspendedSediment, __global float *water)
    {
      int i = get_global_id(0);
      
      
      // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
      float fj = frictionParameter*flowj[i] + deltaT*flowParameter*(terrain[i] + water[i] - terrain[j[i]] - water[j[i]]);
      if (fj<0){
      fj = 0;
      }
      
      float fk = frictionParameter*flowk[i] + deltaT*flowParameter*(terrain[i] + water[i] - terrain[k[i]] - water[k[i]]);
      if (fk<0){
      fk = 0;
      }
      
      float fl = frictionParameter*flowl[i] + deltaT*flowParameter*(terrain[i] + water[i] - terrain[l[i]] - water[l[i]]);
      if (fl<0){
      fl = 0;
      }
      
      // Maximum 50% of water can move in one time step.
      float scalingParameter = 1.0*water[i]/(deltaT*(fj + fk + fl + 0.0001));
      if (scalingParameter > 1){
      scalingParameter = 1;
      }
      fj = fj*scalingParameter;
      fk = fk*scalingParameter;
      fl = fl*scalingParameter;
      
      flowOutj[i] = fj;
      flowOutk[i] = fk;
      flowOutl[i] = fl;
      
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
    
    
    
    __kernel void CalculateSuspendedSedimentFlow(float flowParameter, float deltaT, float frictionParameter,
    __global int *jTarget, __global int *kTarget, __global int *lTarget,
    __global int *j, __global int *k, __global int *l,
    __global float *flowj, __global float *flowk, __global float *flowl,
    __global float * flowOutj, __global float * flowOutk, __global float * flowOutl,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *terrain, __global float *suspendedSediment, __global float *water)
    {
      int i = get_global_id(0);
      
      
      // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
      float fj = frictionParameter*flowj[i] + deltaT*flowParameter*(terrain[i] + water[i] + suspendedSediment[i] - terrain[j[i]] - suspendedSediment[j[i]] - water[j[i]]);
      if (fj<0){
      fj = 0;
      }
      
      float fk = frictionParameter*flowk[i] + deltaT*flowParameter*(terrain[i] + water[i] + suspendedSediment[i] - terrain[k[i]] - suspendedSediment[k[i]] - water[k[i]]);
      if (fk<0){
      fk = 0;
      }
      
      float fl = frictionParameter*flowl[i] + deltaT*flowParameter*(terrain[i] + water[i] + suspendedSediment[i] - terrain[l[i]] - suspendedSediment[l[i]] - water[l[i]]);
      if (fl<0){
      fl = 0;
      }
      
      // Maximum 50% of water can move in one time step.
      float scalingParameter = suspendedSediment[i]/(deltaT*(fj + fk + fl + 0.0001));
      if (scalingParameter > 1){
      scalingParameter = 1;
      }
      fj = fj*scalingParameter;
      fk = fk*scalingParameter;
      fl = fl*scalingParameter;
      
      flowOutj[i] = fj;
      flowOutk[i] = fk;
      flowOutl[i] = fl;
      
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
    
    __kernel void UpdateSuspendedSedimentHeight(float deltaT,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *height, __global float *heightUpdated)
    {
      int i = get_global_id(0);
      
      height[i] = height[i] + deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
    }
    
    
    
    __kernel void TerrainSlippageCalculation(float deltaT, float slippageParameter, float talusAngle, float triangleLength, float minRadius, 
    __global int * jTarget, __global int * kTarget, __global int * lTarget, 
    __global int * j, __global int * k, __global int * l, 
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *height)
    {
        int i = get_global_id(0);
      
        float dHj = height[i] - height[j[i]];
        float dHk = height[i] - height[k[i]];
        float dHl = height[i] - height[l[i]];
        
        float slopej = atan((0.00001+dHj)/(triangleLength * (minRadius+height[i])));
        float slopek = atan((0.00001+dHk)/(triangleLength * (minRadius+height[i])));
        float slopel = atan((0.00001+dHl)/(triangleLength * (minRadius+height[i])));
        
        float fj = 0.0;
        float fk = 0.0;
        float fl = 0.0;
        
        if (slopej > talusAngle){
            fj = deltaT * slippageParameter * (dHj - triangleLength * (minRadius+height[i]) * tan(talusAngle));
        }
        
        if (slopek > talusAngle){
            fk = deltaT * slippageParameter * (dHk - triangleLength * (minRadius+height[i]) * tan(talusAngle));
        }
        
        if (slopel > talusAngle){
            fl = deltaT * slippageParameter * (dHl - triangleLength * (minRadius+height[i]) * tan(talusAngle));
        } 
        
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
    
    __kernel void TerrainSlippageUpdate(float deltaT,
    __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
    __global float *height, __global float *heightUpdated)
    {
      int i = get_global_id(0);
      
      //height[i] = height[i] + deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
    }
    
    
    
    
    
    __kernel void CalculateVelocity(float sqrt3_2,
    __global float * flowInj, __global float * flowInk, __global float * flowInl,
    __global float * flowOutj, __global float * flowOutk, __global float * flowOutl,
    __global float * velocity)
    {
        int i = get_global_id(0);
      
        float vj = flowOutj[i] - flowInj[i];
        float vk = flowOutk[i] - flowInk[i];
        float vl = flowOutl[i] - flowInl[i];
      
        float vx = sqrt3_2*vl - sqrt3_2*vj;
        float vy = 0.5*vj - vk + 0.5*vl;
        
        float v = vj + vk + vl;
        
        velocity[i] = sqrt(vx*vx + vy*vy);
        //velocity[i] = sqrt(vj*vj + vk*vk + vl*vl);
        //velocity[i] = sqrt(v*v);
    }
    
    __kernel void CalculateSlope(float triangleLength, float minRadius,
    __global int * j, __global int * k, __global int * l,
    __global float * height, __global float * suspendedSediment,
    __global float * slope)
    {
        int i = get_global_id(0);
        
        float dHj = height[j[i]] - height[i];
        float dHk = height[k[i]] - height[i];
        float dHl = height[l[i]] - height[i];
        
        if (dHj < 0){
        dHj = -dHj;
        }
        if (dHk < 0){
        dHk = -dHk;
        }        
        if (dHl < 0){
        dHl = -dHl;
        }
        
        float dH = 0.0;
        
        if (dHj > dH){
        dH = dHj;
        }
        if (dHk > dH){
        dH = dHk;
        }        
        if (dHl > dH){
        dH = dHl;
        }
        
        slope[i] = atan((0.00001+dH)/(triangleLength * (minRadius+height[i])));
        //slope[i] = atan((0.00001+dH)/triangleLength);
    }
    
    __kernel void CalculateCarryCapacity(float carryCapacityParameter, 
    __global float * water, __global float * slope, __global float * velocity, __global float * carryCapacity)
    {
        int i = get_global_id(0);

        carryCapacity[i] = carryCapacityParameter * sin(slope[i]) * velocity[i];
        if (carryCapacity[i] > 5.0*water[i]){
            carryCapacity[i] = 5.0*water[i];
        }
    }
    
    __kernel void ErodeDeposit(float deltaT, float erosionRate, float depositionRate,
    __global int * j, __global int * k, __global int * l,
    __global float * terrain, __global float * terrainPrevious, __global float * suspendedSediment, __global float * carryCapacity)
    {
        int i = get_global_id(0);

                if (suspendedSediment[i] < carryCapacity[i]){
                    //Erode
                    float erosionAmount = erosionRate * (carryCapacity[i]-suspendedSediment[i]);

            float Hj = terrainPrevious[j[i]];
            float Hk = terrainPrevious[k[i]];
            float Hl = terrainPrevious[l[i]];
            
            float minH = Hj;
            if (Hk<minH){
                minH = Hk;
            }
            if (Hl<minH){
                minH = Hl;
            }
            
            if (erosionAmount > terrainPrevious[i] - minH){
                erosionAmount = terrainPrevious[i] - minH;
            }
            if (erosionAmount < 0.0){
                erosionAmount = 0.0;
            }
            
            terrain[i] = terrainPrevious[i] - erosionAmount;
            suspendedSediment[i] = suspendedSediment[i] + erosionAmount;
            
            carryCapacity[i] = 1;
        }
        
        if (suspendedSediment[i] > carryCapacity[i]){
            //Deposit
            float depositionAmount = depositionRate * (suspendedSediment[i] - carryCapacity[i]);
            
            //if (depositionAmount < 0.1*suspendedSediment[i]){
            //    depositionAmount = 0.1*suspendedSediment[i];
            //}
            
            float Hj = terrainPrevious[j[i]];
            float Hk = terrainPrevious[k[i]];
            float Hl = terrainPrevious[l[i]];
            
            float maxH = Hj;
            if (Hk>maxH){
                maxH = Hk;
            }
            if (Hl>maxH){
                maxH = Hl;
            }
            
            if (depositionAmount > maxH - terrainPrevious[i]){
                depositionAmount = maxH - terrainPrevious[i];
            }
            if (depositionAmount < 0.0){
                depositionAmount = 0.0;
            }
            //depositionAmount = 0.0;
            
            terrain[i] = terrainPrevious[i] + depositionAmount;
            suspendedSediment[i] = suspendedSediment[i] - depositionAmount;
            //suspendedSediment[i] = 0;
            carryCapacity[i] = 0;
        }
    }
    """).build()

#heightUpdated[j[i]] = heightUpdated[j[i]] + fj;
#heightUpdated[k[i]] = heightUpdated[k[i]] + fk;
#heightUpdated[l[i]] = heightUpdated[l[i]] + fl;
#heightUpdated[i] = heightUpdated[i] - fj - fk - fl;

# Sets up lists needed to update the triangle vertices.
from scipy.spatial import cKDTree
kdTree = cKDTree(world.unscaledFaceCoordinates)
rTypical, i = kdTree.query(world.unscaledVertices[0, :])
rQuery, queryResult = kdTree.query(world.unscaledVertices[:, :], k=6)
queryResult = np.array(queryResult)

# Sets up animation
terrainVertices = world.unscaledVertices.copy()
suspendedSedimentVertices = world.unscaledVertices.copy()
waterVertices = world.unscaledVertices.copy()


        rRock = rockHeight[queryResult]
        r = self.world.minRadius + np.sum(rRock[:, :, 0], axis=1) / 6
        self.rockVertices[:, 0] = r * self.world.unscaledVertices[:, 0]
        self.rockVertices[:, 1] = r * self.world.unscaledVertices[:, 1]
        self.rockVertices[:, 2] = r * self.world.unscaledVertices[:, 2]

        rSediment = sedimentHeight[queryResult]
        r = self.world.minRadius + np.sum(rRock[:, :, 0], axis=1) / 6 + np.sum(rSediment[:, :, 0], axis=1) / 6 - self.sedimentOffset
        self.sedimentVertices[:, 0] = r * self.world.unscaledVertices[:, 0]
        self.sedimentVertices[:, 1] = r * self.world.unscaledVertices[:, 1]
        self.sedimentVertices[:, 2] = r * self.world.unscaledVertices[:, 2]

rWater = waterHeight[queryResult]
r = 10 + np.sum(rTerrain[:, :, 0] + rWater, axis=1)/6 + np.sum(rSuspendedSediment, axis=1) / 6 - waterMinimumVisualDepth
waterVertices[:, 0] = r * world.unscaledVertices[:, 0]
waterVertices[:, 1] = r * world.unscaledVertices[:, 1]
waterVertices[:, 2] = r * world.unscaledVertices[:, 2]

        self.rockHeight = rock
        self.sedimentHeight = sediment
        self.waterHeight = water

        self.deltaT = np.array(deltaT).astype(np.float32)
        self.flowParameter = np.array(waterFlowSpeed).astype(np.float32)
        self.frictionParameter = np.array(waterFlowFriction).astype(np.float32)

        sedimentFrictionParameter = np.array(0.98)
        sedimentFrictionParameter = sedimentFrictionParameter.astype(np.float32)

        self.thermalErosionRate = np.array(thermalErosionRate).astype(np.float32)
        self.thermalErosionSedimentLimit = np.array(sedimentErosionLimit).astype(np.float32)
        self.rockToSedimentExpansionFactor = np.array(rockToSedimentExpansion).astype(np.float32)

        minRadius = np.array(np.min(world.faceRadius))
        self.minRadius = minRadius.astype(np.float32)

waterHeight *= 0

for i in range(nIterations):

    print('total amount of material: ', np.sum(terrainHeight) + np.sum(suspendedSediment))

    #waterHeight[np.random.randint(0, np.size(world.f, 0))] += 10


    if i>stopRainIteration:
        #carryCapacityParameter = np.array(0.0)
        #carryCapacityParameter = carryCapacityParameter.astype(np.float32)
        rainAmount = 0
        carryCapacityParameter = np.array(0.0)
        carryCapacityParameter = carryCapacityParameter.astype(np.float32)
    else:
        rainAmount = maxRainAmount * np.sin(2*np.pi*i/200)**2
    waterHeight += deltaT*rainAmount

    heightUpdated = np.zeros_like(world.faceRadius, dtype=np.float32)
    #heightUpdated = height.copy()
    flowUpdatedj = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowUpdatedk = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowUpdatedl = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowUpdatedj = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowUpdatedk = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowUpdatedl = np.zeros_like(world.faceRadius, dtype=np.float32)

    flowInj = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowInk = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowInl = np.zeros_like(world.faceRadius, dtype=np.float32)
    flowOut = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowInj = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowInk = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowInl = np.zeros_like(world.faceRadius, dtype=np.float32)
    sedimentFlowOut = np.zeros_like(world.faceRadius, dtype=np.float32)

    flowj_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowj)
    flowk_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowk)
    flowl_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flowl)
    flowUpdatedj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedj.nbytes)
    flowUpdatedk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedk.nbytes)
    flowUpdatedl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedl.nbytes)
    sedimentFlowj_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=sedimentFlowj)
    sedimentFlowk_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=sedimentFlowk)
    sedimentFlowl_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=sedimentFlowl)
    sedimentFlowUpdatedj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedj.nbytes)
    sedimentFlowUpdatedk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedk.nbytes)
    sedimentFlowUpdatedl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowUpdatedl.nbytes)

    #flowInj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInj.nbytes)
    #flowInk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInk.nbytes)
    #flowInl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInl.nbytes)
    #flowOut_buf = cl.Buffer(ctx, mf.READ_WRITE, flowOut.nbytes)
    flowInj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInj.nbytes)
    flowInk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInk.nbytes)
    flowInl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInl.nbytes)
    flowOut_buf = cl.Buffer(ctx, mf.WRITE_ONLY, flowOut.nbytes)
    sedimentFlowInj_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInj.nbytes)
    sedimentFlowInk_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInk.nbytes)
    sedimentFlowInl_buf = cl.Buffer(ctx, mf.READ_WRITE, flowInl.nbytes)
    sedimentFlowOut_buf = cl.Buffer(ctx, mf.READ_WRITE, flowOut.nbytes)

    terrainHeight_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=terrainHeight)
    waterHeight_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=waterHeight)
    #heightUpdated_buf = cl.Buffer(ctx, mf.WRITE_ONLY, heightUpdated.nbytes)
    heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE, heightUpdated.nbytes)
    velocity_buf = cl.Buffer(ctx, mf.READ_WRITE, velocity.nbytes)
    slope_buf = cl.Buffer(ctx, mf.READ_WRITE, slope.nbytes)
    carryCapacity_buf = cl.Buffer(ctx, mf.READ_WRITE, slope.nbytes)
    #heightUpdated_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=heightUpdated)

    tic = time.time()
    prg.CalculateWaterFlow(queue, heightUpdated.shape, None, flowParameter, deltaT, frictionParameter,
                           jTarget_buf, kTarget_buf, lTarget_buf, j_buf, k_buf, l_buf,
                           flowj_buf, flowk_buf, flowl_buf, flowUpdatedj_buf, flowUpdatedk_buf, flowUpdatedl_buf,
                           flowInj_buf, flowInk_buf, flowInl_buf, flowOut_buf, terrainHeight_buf, suspendedSediment_buf, waterHeight_buf)
    toc = time.time()
    print('pyopencl water flow calculation time : ', toc-tic)

    tic = time.time()
    prg.CalculateSuspendedSedimentFlow(queue, heightUpdated.shape, None, sedimentFlowParameter, deltaT, sedimentFrictionParameter,
                           jTarget_buf, kTarget_buf, lTarget_buf, j_buf, k_buf, l_buf,
                           sedimentFlowj_buf, sedimentFlowk_buf, sedimentFlowl_buf,
                           sedimentFlowUpdatedj_buf, sedimentFlowUpdatedk_buf, sedimentFlowUpdatedl_buf,
                           sedimentFlowInj_buf, sedimentFlowInk_buf, sedimentFlowInl_buf, sedimentFlowOut_buf,
                           terrainHeight_buf, suspendedSediment_buf, waterHeight_buf)
    toc = time.time()
    print('pyopencl suspended sediment flow calculation time : ', toc-tic)

    tic = time.time()
    prg.UpdateWaterHeight(queue, heightUpdated.shape, None, deltaT, flowInj_buf, flowInk_buf, flowInl_buf, flowOut_buf,
                            waterHeight_buf, heightUpdated_buf)
    toc = time.time()
    print('pyopencl water update time : ', toc-tic)

    tic = time.time()
    prg.UpdateSuspendedSedimentHeight(queue, heightUpdated.shape, None, deltaT, sedimentFlowInj_buf, sedimentFlowInk_buf, sedimentFlowInl_buf, sedimentFlowOut_buf,
                            suspendedSediment_buf, heightUpdated_buf)
    toc = time.time()
    print('pyopencl suspended sediment update time : ', toc-tic)

    tic = time.time()
    prg.CalculateVelocity(queue, heightUpdated.shape, None, sqrt3_2, flowInj_buf, flowInk_buf, flowInl_buf, flowUpdatedj_buf, flowUpdatedk_buf, flowUpdatedl_buf, velocity_buf)
    toc = time.time()
    print('pyopencl velocity calculation time : ', toc-tic)

            self.kernel.kernels.CalculateWaterFlow(self.kernel.queue, self.heightUpdated.shape, None, self.flowParameter, self.deltaT, self.frictionParameter,
                                               self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                               self.waterFlowj_buf, self.waterFlowk_buf, self.waterFlowl_buf, self.waterFlowUpdatedj_buf,
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


            self.kernel.kernels.SedimentSlippageCalculation(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.slippageParameter,
                                                        self.talusAngle, self.triangleLength, self.minRadius,
                                                        self.jTarget_buf, self.kTarget_buf, self.lTarget_buf, self.j_buf, self.k_buf, self.l_buf,
                                                        self.sedimentFlowInj_buf, self.sedimentFlowInk_buf, self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                                        self.terrainHeight_buf, self.sedimentHeight_buf, self.slope_buf)
            self.kernel.kernels.SedimentSlippageUpdate(self.kernel.queue, self.heightUpdated.shape, None, self.deltaT, self.sedimentFlowInj_buf,
                                                   self.sedimentFlowInk_buf, self.sedimentFlowInl_buf, self.sedimentFlowOut_buf,
                                                   self.sedimentHeight_buf)

    cl.enqueue_copy(queue, terrainHeight, terrainHeight_buf)
    terrainHeightPrevious = terrainHeight.copy()
    terrainHeightPrevious = terrainHeightPrevious.astype(np.float32)
    terrainHeightPrevious_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=terrainHeightPrevious)

    tic = time.time()
    prg.ErodeDeposit(queue, heightUpdated.shape, None, deltaT, erosionRate, depositionRate, j_buf, k_buf, l_buf, terrainHeight_buf, terrainHeightPrevious_buf, suspendedSediment_buf, carryCapacity_buf)
    toc = time.time()
    print('pyopencl erode/deposit calculation time : ', toc-tic)

    cl.enqueue_copy(queue, sedimentFlowInj, sedimentFlowInj_buf)

    #cl.enqueue_copy(queue, heightUpdated, heightUpdated_buf)
    cl.enqueue_copy(queue, velocity, velocity_buf)
    cl.enqueue_copy(queue, slope, slope_buf)

            cl.enqueue_copy(self.kernel.queue, self.rockHeight, self.terrainHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.sedimentHeight, self.sedimentHeight_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterHeight, self.heightUpdated_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowj, self.waterFlowUpdatedj_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowk, self.waterFlowUpdatedk_buf)
            cl.enqueue_copy(self.kernel.queue, self.waterFlowl, self.waterFlowUpdatedl_buf)

            cl.enqueue_copy(self.kernel.queue, self.streamPower, self.streamPower_buf)

            cl.enqueue_copy(self.kernel.queue, self.sedimentVertices, self.landVertices_buf)

    #cl.enqueue_copy(queue, flowInj, flowInj_buf)
    #cl.enqueue_copy(queue, flowInk, flowInk_buf)
    #cl.enqueue_copy(queue, flowInl, flowInl_buf)
    #cl.enqueue_copy(queue, flowOut, flowOut_buf)

    #velocity = flowInj + flowInk + flowInl
    #velocity = flowj + flowk + flowl

    tic = time.time()
    # Evaporation
    waterHeight *= (1 - evaporationRate * deltaT)
    toc = time.time()
    print('water evaporation time : ', toc-tic)

    print(np.min(velocity))
    print(np.mean(velocity))
    print(np.max(velocity))
    print('----')
    print(np.min(slope))
    print(np.mean(slope))
    print(np.max(slope))
    print('----')
    print(np.min(terrainHeight))
    print(np.mean(terrainHeight))
    print(np.max(terrainHeight))
    print('----')
    print(np.min(suspendedSediment))
    print(np.mean(suspendedSediment))
    print(np.max(suspendedSediment))

    #height = heightUpdated

    #print('------------------------------------------------------------------')

    if animate and i%animationUpdateInterval == 0:
        #plotter.update_scalars(waterHeight, mesh=waterMesh, render=False)
        if animateTopography:
            rTerrain = terrainHeight[queryResult]
            r = 10 + np.sum(rTerrain[:, :, 0], axis=1) / 6
            terrainVertices[:, 0] = r * world.unscaledVertices[:, 0]
            terrainVertices[:, 1] = r * world.unscaledVertices[:, 1]
            terrainVertices[:, 2] = r * world.unscaledVertices[:, 2]

            rSuspendedSediment = suspendedSediment[queryResult]
            r = 10 + np.sum(rTerrain[:, :, 0] + rSuspendedSediment, axis=1) / 6 - \
                suspendedSedimentMinimumVisualDepth
            suspendedSedimentVertices[:, 0] = r * world.unscaledVertices[:, 0]
            suspendedSedimentVertices[:, 1] = r * world.unscaledVertices[:, 1]
            suspendedSedimentVertices[:, 2] = r * world.unscaledVertices[:, 2]

            rWater = waterHeight[queryResult]
            r = 10 + np.sum(rTerrain[:, :, 0] + rSuspendedSediment + rWater, axis=1)/6 -\
                waterMinimumVisualDepth-5
            waterVertices[:, 0] = r * world.unscaledVertices[:, 0]
            waterVertices[:, 1] = r * world.unscaledVertices[:, 1]
            waterVertices[:, 2] = r * world.unscaledVertices[:, 2]


            #cl.enqueue_copy(queue, velocity, carryCapacity_buf)


            #plotter.update_scalars(slope, mesh=terrainMesh, render=False)
            plotter.update_scalars(velocity, mesh=waterMesh, render=False)
            plotter.update_coordinates(points=terrainVertices, mesh=terrainMesh)
            plotter.update_coordinates(points=suspendedSedimentVertices, mesh=suspendedSedimentMesh)
            plotter.update_coordinates(points=waterVertices, mesh=waterMesh)

            terrainMesh.compute_normals(point_normals=True, inplace=True)
            #suspendedSedimentMesh.compute_normals(point_normals=True, inplace=True)
            waterMesh.compute_normals(point_normals=True, inplace=True)


        #plotter.render()
    print(' ')
tocTotalSimulation = time.time()

print('terrain amount : ', np.sum(terrainHeight))
print('sediment amount : ', np.sum(suspendedSediment))
print('water amount : ', np.sum(waterHeight))

print('Total simulation time : ', tocTotalSimulation-ticTotalSimulation)
print('Simulation done')
#plotter.update_scalars(waterHeight, mesh=waterMesh, render=False)
if animateTopography:
    rTerrain = terrainHeight[queryResult]
    r = 10 + np.sum(rTerrain[:, :, 0], axis=1) / 6
    terrainVertices[:, 0] = r * world.unscaledVertices[:, 0]
    terrainVertices[:, 1] = r * world.unscaledVertices[:, 1]
    terrainVertices[:, 2] = r * world.unscaledVertices[:, 2]

    rSuspendedSediment = suspendedSediment[queryResult]
    r = 10 + np.sum(rTerrain[:, :, 0] + rSuspendedSediment, axis=1) / 6 - \
        suspendedSedimentMinimumVisualDepth
    suspendedSedimentVertices[:, 0] = r * world.unscaledVertices[:, 0]
    suspendedSedimentVertices[:, 1] = r * world.unscaledVertices[:, 1]
    suspendedSedimentVertices[:, 2] = r * world.unscaledVertices[:, 2]

    rWater = waterHeight[queryResult]
    r = 10 + np.sum(rTerrain[:, :, 0] + rWater, axis=1) / 6 - \
        waterMinimumVisualDepth
    waterVertices[:, 0] = r * world.unscaledVertices[:, 0]
    waterVertices[:, 1] = r * world.unscaledVertices[:, 1]
    waterVertices[:, 2] = r * world.unscaledVertices[:, 2]

    print('Rock Amount =     ', np.sum(erosion.rockHeight))
    print('Sediment Amount = ', np.sum(erosion.sedimentHeight))
    print('Water Amount =    ', np.sum(erosion.waterHeight))

    # Save topography to file.

    world.v = visualizer.rockVertices
    world.vertexRadius = world.CalculateVertexRadius(world.v)
    world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
    pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldRock_15.pkl', "wb"))

world.v = 10*waterVertices
world.vertexRadius = world.CalculateVertexRadius(world.v)
world.faceRadius = world.CalculateFaceRadius(world.v, world.f)
pickle.dump(world, open(Root_Directory.Path() + '/Data/tmp_Data/worldWater_12.pkl', "wb"))

    visualizer.plotter.render()
    visualizer.plotter.show(auto_close=False)

# ================================================================================================================
# ================================================================================================================
# ================================================================================================================

if False:
    import matplotlib.pyplot as plt
    x = [52020, 204020, 1812020 , 5020020]
    y = [10, 35, 241, 627]

    plt.plot(x, y)
    plt.scatter(x, y)
    plt.show()
    quit()
    #   divisions    #triangles    time(s)    iterations
    #       50           52020       10          1000
    #      100          204020       35          1000
    #      300         1812020      241          1000
    #      500         5020020      627          1000
    #

def VisualizeLoadedWorld(fileToOpen):
    erodedWorld = pickle.load(open(Root_Directory.Path() + '/Data/tmp_Data/erodedWorld_' + fileToOpen + '.pkl', "rb"))

    print('#Triangles : ', np.size(erodedWorld.world.f, 0))

    rockMesh = pv.PolyData(erodedWorld.rock, np.hstack(erodedWorld.world.f))
    sedimentMesh = pv.PolyData(erodedWorld.sediment, np.hstack(erodedWorld.world.f))
    waterMesh = pv.PolyData(erodedWorld.water, np.hstack(erodedWorld.world.f))

    plotter = pv.Plotter()
    plotter.add_mesh(rockMesh, smooth_shading=False, color=(0.2, 0.15, 0.15, 1))
    plotter.add_mesh(sedimentMesh, smooth_shading=False, color=(0.35, 0.3, 0.25, 1))
    #plotter.add_mesh(waterMesh, smooth_shading=True, color=(0.05, 0.2, 0.35, 1))
    plotter.add_mesh(waterMesh, smooth_shading=False, color=(0.05, 0.15, 0.25, 1))

    #plotter.enable_eye_dome_lighting()
    plotter.show(auto_close=False)


