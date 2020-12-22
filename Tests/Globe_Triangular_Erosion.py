import pyvista as pv
import numpy as np
import pyopencl as cl
import time
import pickle
from scipy.spatial import cKDTree

import Library.World as World
import Root_Directory

class OpenclKernel():
    def __init__(self, mode = 1):
        if mode == 1:
            self.Initialize1()
        elif mode == 2:
            self.Initialize2()

    def Initialize1(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
        self.kernels = cl.Program(self.ctx, """
            __kernel void CalculateWaterFlow(float flowParameter, float deltaT, float frictionParameter,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float *flowj, __global float *flowk, __global float *flowl,
            __global float * flowOutj, __global float * flowOutk, __global float * flowOutl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *water)
            {
              int i = get_global_id(0);


              // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
              float dHj = rock[i] + sediment[i] + water[i] - rock[j[i]] - sediment[j[i]] - water[j[i]];
              float dHk = rock[i] + sediment[i] + water[i] - rock[k[i]] - sediment[k[i]] - water[k[i]];
              float dHl = rock[i] + sediment[i] + water[i] - rock[l[i]] - sediment[l[i]] - water[l[i]];

              //float fj = deltaT*flowParameter*dHj;
              //float fk = deltaT*flowParameter*dHk;
              //float fl = deltaT*flowParameter*dHl;

              //float depthParameter = (water[i]-0.4)/0.2;
              float depthParameter;
              if (water[i]<0.1)
              {
                depthParameter = 0.0;
              }else
              {
                depthParameter = (water[i]-0.1)/0.2;
              }
              if (depthParameter > 1.0)
              {
                depthParameter = 1.0;
              }


              //float depthParameter = water[i]/0.2;
              //if (depthParameter > 0.3)
              //{
              //  depthParameter = 1.0;
              //}
              //if (depthParameter < 0.1)
              //{
              //  depthParameter = 0.0;
              //}

              //float fj = frictionParameter*flowj[i] + deltaT*flowParameter*dHj;
              //float fk = frictionParameter*flowk[i] + deltaT*flowParameter*dHk;
              //float fl = frictionParameter*flowl[i] + deltaT*flowParameter*dHl;
              float fj = (frictionParameter-0.1*depthParameter)*flowj[i] + deltaT*flowParameter*dHj;
              float fk = (frictionParameter-0.1*depthParameter)*flowk[i] + deltaT*flowParameter*dHk;
              float fl = (frictionParameter-0.1*depthParameter)*flowl[i] + deltaT*flowParameter*dHl;


              //float fj = depthParameter * deepfj + (1-depthParameter)*shallowfj;
              //float fk = depthParameter * deepfk + (1-depthParameter)*shallowfk;
              //float fl = depthParameter * deepfl + (1-depthParameter)*shallowfl;

              // Water flow is not allowed up-hill.
              if (dHj<0 || fj<0 ){
                fj = 0;
              }
              if (dHk<0 || fk<0){
                fk = 0;
              }
              if (dHl<0 || fl<0){
                fl = 0;
              }

              //if (fj<0){
              //  fj = 0;
              //}
              //if (fk<0){
              //  fk = 0;
              //}
              //if (fl<0){
              //  fl = 0;
              //}

              // The flow is scaled such that no more water can leave the cell than exist in the cell.
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
            __global float * velocity, __global float * water, __global float * waterUpdated)
            {
                int i = get_global_id(0);

                float vj = flowOutj[i] - flowInj[i];
                float vk = flowOutk[i] - flowInk[i];
                float vl = flowOutl[i] - flowInl[i];

                float vx = sqrt3_2*vl - sqrt3_2*vj;
                float vy = 0.5*vj - vk + 0.5*vl;

                float v = vj + vk + vl;

                //float meanWater = (water[i] + waterUpdated[i])/2;
                //float meanWater = water[i];

                velocity[i] = sqrt(vx*vx + vy*vy);
                //velocity[i] = sqrt(vj*vj + vk*vk + vl*vl);
                //velocity[i] = sqrt(v*v);
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

            __kernel void CalculateCarryCapacity(float carryCapacityParameter, 
            __global float * water, __global float * slope, __global float * velocity, __global float * carryCapacity)
            {
                int i = get_global_id(0);

                carryCapacity[i] = carryCapacityParameter * sin(slope[i]) * velocity[i];
                if (carryCapacity[i] > 5.0*water[i]){
                    carryCapacity[i] = 5.0*water[i];
                }
            }

             __kernel void CalculateStreamPower(float streamPowerParameter, 
            __global float * water, __global float * slope, __global float * velocity, __global float * streamPower)
            {
                int i = get_global_id(0);

                //streamPower[i] = streamPowerParameter * sin(slope[i]) * velocity[i];
                streamPower[i] = streamPowerParameter * slope[i] * velocity[i];
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


            __kernel void HydrolicErosion(float deltaT, float sedimentLimit, float expansionFactor, float minErosionRate, float erosionRate, __global float * rockResistivity, 
                                        __global int * j, __global int * k, __global int * l,
                                        __global float * slope, __global float * velocity, __global float * streamPower, 
                                        __global float * rock, __global float * sediment, __global float * water)
            {
                //
                // Rock -> sediment 
                // Erosion speed is increased by slope, and is only performed when sediment is below a limit.
                // There is a limit on how much can be eroded such that no "holes" can be dug, the rock height can not be reduced below it's lowest neighbour.
                //
                int i = get_global_id(0);

                float dHj = rock[i] - rock[j[i]];
                float dHk = rock[i] - rock[k[i]];
                float dHl = rock[i] - rock[l[i]];

                float dHMax = 0.0;
                if (dHj > dHMax)
                {
                    dHMax = dHj;
                }
                if (dHk > dHMax)
                {
                    dHMax = dHk;
                }
                if (dHl > dHMax)
                {
                    dHMax = dHl;
                }
                if (sedimentLimit - sediment[i]>0)
                {
                    if (dHMax > sedimentLimit - sediment[i])
                    {
                        dHMax = sedimentLimit - sediment[i];
                    }
                }else
                {
                    dHMax = 0.0;
                }

                float erosionAmount = 0.0;
                //if (sediment[i] < sedimentLimit && streamPower[i]>rockResistivity[i]){
                if (dHMax > 0.0){
                    //erosionAmount = deltaT*erosionRate*(streamPower[i]/rockResistivity-1);
                    //erosionAmount = 1000*deltaT*water[i]*erosionRate*(streamPower[i]-rockResistivity[i]);

                    //erosionAmount = deltaT*erosionRate*(streamPower[i]-rockResistivity[i]);
                    //erosionAmount = deltaT*erosionRate*streamPower[i]*streamPower[i]/(1+rockResistivity[i]);
                    erosionAmount = deltaT*erosionRate*streamPower[i]/(1+rockResistivity[i]);
                }else{
                    erosionAmount = deltaT*erosionRate*minErosionRate;
                }

                if (erosionAmount > dHMax)
                {
                    erosionAmount = dHMax;
                }

                rock[i] = rock[i] - erosionAmount;
                sediment[i] = sediment[i] + expansionFactor * erosionAmount;


                //if (sediment[i] < sedimentLimit){
                //    float erosionAmount = deltaT*erosionRate*streamPower[i];
                //    rock[i] = rock[i] - erosionAmount;
                //    sediment[i] = sediment[i] + expansionFactor * erosionAmount;
                //}
            }

            __kernel void ThermalErosion(float deltaT, float thermalErosionRate, float sedimentLimit, float expansionFactor, float talusSlope,
            __global float * rock, __global float * sediment, __global float * water, __global float * slope)
            {
                //
                // Rock -> sediment 
                // Erosion speed is increased by slope, and is only performed when sediment is below a limit.
                //
                int i = get_global_id(0);

                if (sediment[i] < sedimentLimit && water[i] < sedimentLimit && slope[i] > talusSlope){
                    float erosionAmount = 0.02*(slope[i]-talusSlope)*deltaT*thermalErosionRate;
                    //float erosionAmount = 0.02*deltaT*thermalErosionRate;
                    rock[i] = rock[i] - erosionAmount;
                    sediment[i] = sediment[i] + expansionFactor * erosionAmount;
                }
            }

            __kernel void SedimentSlippageCalculation(float deltaT, float slippageRate, float talusAngle, float triangleLength, float minRadius, 
            __global int * jTarget, __global int * kTarget, __global int * lTarget, 
            __global int * j, __global int * k, __global int * l, 
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *slope)
            {
                int i = get_global_id(0);

                float dHj = rock[i] + sediment[i] - rock[j[i]] - sediment[j[i]];
                float dHk = rock[i] + sediment[i] - rock[k[i]] - sediment[k[i]];
                float dHl = rock[i] + sediment[i] - rock[l[i]] - sediment[l[i]];

                float slopej = atan((0.00001+dHj)/(triangleLength * (minRadius+rock[i]+sediment[i])));
                float slopek = atan((0.00001+dHk)/(triangleLength * (minRadius+rock[i]+sediment[i])));
                float slopel = atan((0.00001+dHl)/(triangleLength * (minRadius+rock[i]+sediment[i])));

                float fj = 0.0;
                float fk = 0.0;
                float fl = 0.0;

                //if (slopej > talusAngle){
                //    fj = deltaT * slippageRate * (dHj - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //}
                //if (slopek > talusAngle){
                //    fk = deltaT * slippageRate * (dHk - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //}
                //if (slopel > talusAngle){
                //    fl = deltaT * slippageRate * (dHl - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //} 


                if (slope[i]>talusAngle)
                {
                    if (dHj > 0)
                    {
                        fj = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fj>dHj){fj = dHj;}
                    }
                    if (dHk > 0)
                    {
                        fk = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fk>dHk){fk = dHk;}
                    }
                    if (dHl > 0)
                    {
                        fl = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fl>dHl){fl = dHl;}
                    }
                }

                float scalingParameter = 0.5*sediment[i]/(deltaT*(fj + fk + fl + 0.0001));
                if (scalingParameter > 1){
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

            __kernel void SedimentSlippageUpdate(float deltaT,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *height)
            {
              int i = get_global_id(0);

              height[i] = height[i] + deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
            }

            __kernel void SedimentFlow(float deltaT, float flowRate, float sedimentResistivity,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float *waterFlowj, __global float *waterFlowk, __global float *waterFlowl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *slope, __global float *streamPower)
            {
              int i = get_global_id(0);

              float sedimentFlowFactor = flowRate * streamPower[i];
              //float sedimentFlowFactor = 0.0;
              //if (streamPower[i]>sedimentResistivity){
              //  //sedimentFlowFactor = flowRate * (streamPower[i]/sedimentResistivity-1);
              //  sedimentFlowFactor = flowRate * (streamPower[i]-sedimentResistivity);
              //} else {
              //  sedimentFlowFactor = 0.0;
              //}

              float dHj = rock[i] + sediment[i] - rock[j[i]] - sediment[j[i]];
              float dHk = rock[i] + sediment[i] - rock[k[i]] - sediment[k[i]];
              float dHl = rock[i] + sediment[i] - rock[l[i]] - sediment[l[i]];

              // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
              float fj = sedimentFlowFactor * waterFlowj[i];
              //float fj = deltaT*sedimentFlowFactor * dHj;
              if (fj<0){  
              fj = 0;  
              }  

              float fk = sedimentFlowFactor * waterFlowk[i];
              //float fk = deltaT*sedimentFlowFactor * dHk;
              if (fk<0){  
              fk = 0;  
              }  

              float fl = sedimentFlowFactor * waterFlowl[i];
              //float fl = deltaT*sedimentFlowFactor * dHl;
              if (fl<0){
              fl = 0;
              }

              if (dHj < 0.0){
                fj = 0.0;
              }
              if (dHk < 0.0){
                fk = 0.0;
              }
              if (dHl < 0.0){
                fl = 0.0;
              }

              float scalingParameter = 0.5*sediment[i]/(deltaT*(fj + fk + fl + 0.0001));
              if (scalingParameter > 1){
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

            __kernel void UpdateVertices(int nVertices, float minRadius,
            __global int * facesConnectingToVertex, __global float * unscaledVertices,
            __global float * sedimentVertices, __global float * waterVertices,
            __global float * rock, __global float * sediment, __global float * water)
            {
                int i = get_global_id(0);

                float sedimentRadius = 0.0;
                float waterRadius = 0.0;
                for (int iFace = 0; iFace < 6; iFace++)
                {
                    sedimentRadius += rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]];
                    waterRadius += rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]] + water[facesConnectingToVertex[iFace + i*6]];
                }
                sedimentRadius /= 6.0;
                sedimentRadius += minRadius;
                waterRadius /= 6.0;
                waterRadius += minRadius;

                for (int iDimension = 0; iDimension < 3; iDimension++)
                {
                    sedimentVertices[iDimension + i*3] = sedimentRadius * unscaledVertices[iDimension + i*3];
                    waterVertices[iDimension + i*3] = waterRadius * unscaledVertices[iDimension + i*3];
                }
            }

            __kernel void UpdateVisualizationVertices(int nVertices, float minRadius, float sedimentOffset, float waterOffset,
            __global int * facesConnectingToVertex, __global float * unscaledVertices,
            __global float * rockVertices, __global float * sedimentVertices, __global float * waterVertices,
            __global float * rock, __global float * sediment, __global float * water)
            {
                int i = get_global_id(0);

                float rockRadius = 0.0;
                float sedimentRadius = 0.0;
                float waterRadius = 0.0;
                for (int iFace = 0; iFace < 6; iFace++)
                {
                    rockRadius += rock[facesConnectingToVertex[iFace + i*6]];

                    float sedimentRadiusTmp = rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]];
                    if (sedimentRadiusTmp - sedimentOffset < rockRadius)
                    {
                        sedimentRadiusTmp -= sedimentOffset;
                    }
                    sedimentRadius += sedimentRadiusTmp;

                    float waterRadiusTmp = rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]] + water[facesConnectingToVertex[iFace + i*6]];
                    if (waterRadiusTmp - waterOffset < rockRadius || waterRadiusTmp - waterOffset < sedimentRadius)
                    {
                        waterRadiusTmp -= waterOffset;
                    }
                    waterRadius += waterRadiusTmp;
                }
                rockRadius /= 6.0;
                rockRadius += minRadius;
                sedimentRadius /= 6.0;
                sedimentRadius += minRadius;
                waterRadius /= 6.0;
                waterRadius += minRadius;

                for (int iDimension = 0; iDimension < 3; iDimension++)
                {
                    rockVertices[iDimension + i*3] = rockRadius * unscaledVertices[iDimension + i*3];
                    sedimentVertices[iDimension + i*3] = sedimentRadius * unscaledVertices[iDimension + i*3];
                    waterVertices[iDimension + i*3] = waterRadius * unscaledVertices[iDimension + i*3];
                }
            }
            """).build()
    def Initialize2(self):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags
        self.kernels = cl.Program(self.ctx, """
            __kernel void CalculateWaterFlow(float flowParameter, float deltaT, float frictionParameter,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float *flowj, __global float *flowk, __global float *flowl,
            __global float * flowOutj, __global float * flowOutk, __global float * flowOutl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *water)
            {
              int i = get_global_id(0);


              // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
              float dHj = rock[i] + sediment[i] + water[i] - rock[j[i]] - sediment[j[i]] - water[j[i]];
              float dHk = rock[i] + sediment[i] + water[i] - rock[k[i]] - sediment[k[i]] - water[k[i]];
              float dHl = rock[i] + sediment[i] + water[i] - rock[l[i]] - sediment[l[i]] - water[l[i]];


              //float depthParameter = water[i]/0.2;
              //if (depthParameter > 0.3)
              //{
              //  depthParameter = 1.0;
              //}
              //if (depthParameter < 0.1)
              //{
              //  depthParameter = 0.0;
              //}

              float fj = frictionParameter*flowj[i] + deltaT*flowParameter*dHj;
              float fk = frictionParameter*flowk[i] + deltaT*flowParameter*dHk;
              float fl = frictionParameter*flowl[i] + deltaT*flowParameter*dHl;


              // Water flow is not allowed up-hill.
              //if (dHj<0 || fj<0 ){
              //  fj = 0;
              //}
              //if (dHk<0 || fk<0){
              //  fk = 0;
              //}
              //if (dHl<0 || fl<0){
              //  fl = 0;
              //}

              if (fj<0){
                fj = 0;
              }
              if (fk<0){
                fk = 0;
              }
              if (fl<0){
                fl = 0;
              }

              // The flow is scaled such that no more water can leave the cell than exist in the cell.
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
            __global float * velocity, __global float * water, __global float * waterUpdated)
            {
                int i = get_global_id(0);

                float vj = flowOutj[i] - flowInj[i];
                float vk = flowOutk[i] - flowInk[i];
                float vl = flowOutl[i] - flowInl[i];

                float vx = sqrt3_2*vl - sqrt3_2*vj;
                float vy = 0.5*vj - vk + 0.5*vl;

                float v = vj + vk + vl;

                //float meanWater = (water[i] + waterUpdated[i])/2;
                //float meanWater = water[i];

                velocity[i] = sqrt(vx*vx + vy*vy);
                //velocity[i] = (velocity[i] + sqrt(vx*vx + vy*vy))/2;
                //velocity[i] = sqrt(vj*vj + vk*vk + vl*vl);
                //velocity[i] = sqrt(v*v);
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

            __kernel void CalculateCarryCapacity(float carryCapacityParameter, 
            __global float * water, __global float * slope, __global float * velocity, __global float * carryCapacity)
            {
                int i = get_global_id(0);

                carryCapacity[i] = carryCapacityParameter * sin(slope[i]) * velocity[i];
                if (carryCapacity[i] > 5.0*water[i]){
                    carryCapacity[i] = 5.0*water[i];
                }
            }

             __kernel void CalculateStreamPower(float streamPowerParameter, 
            __global float * water, __global float * slope, __global float * velocity, __global float * streamPower)
            {
                int i = get_global_id(0);

                //streamPower[i] = streamPowerParameter * sin(slope[i]) * velocity[i];
                streamPower[i] = streamPowerParameter * slope[i] * velocity[i];
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


            __kernel void HydrolicErosion(float deltaT, float sedimentLimit, float expansionFactor, float minErosionRate, float erosionRate, __global float * rockResistivity, 
                                        __global int * j, __global int * k, __global int * l,
                                        __global float * slope, __global float * velocity, __global float * streamPower, 
                                        __global float * rock, __global float * sediment, __global float * water)
            {
                //
                // Rock -> sediment 
                // Erosion speed is increased by slope, and is only performed when sediment is below a limit.
                // There is a limit on how much can be eroded such that no "holes" can be dug, the rock height can not be reduced below it's lowest neighbour.
                //
                int i = get_global_id(0);

                float dHj = rock[i] - rock[j[i]];
                float dHk = rock[i] - rock[k[i]];
                float dHl = rock[i] - rock[l[i]];

                float dHMax = 0.0;
                if (dHj > dHMax)
                {
                    dHMax = dHj;
                }
                if (dHk > dHMax)
                {
                    dHMax = dHk;
                }
                if (dHl > dHMax)
                {
                    dHMax = dHl;
                }
                if (sedimentLimit - sediment[i]>0)
                {
                    if (dHMax > sedimentLimit - sediment[i])
                    {
                        dHMax = sedimentLimit - sediment[i];
                    }
                }else
                {
                    dHMax = 0.0;
                }

                float erosionAmount = 0.0;
                //if (sediment[i] < sedimentLimit && streamPower[i]>rockResistivity[i])
                //if (dHMax > 0.0)
                //if (streamPower[i]>rockResistivity[i])
                if (streamPower[i]>0.0)
                {
                    //erosionAmount = deltaT*erosionRate*(streamPower[i]/rockResistivity-1);
                    //erosionAmount = 1000*deltaT*water[i]*erosionRate*(streamPower[i]-rockResistivity[i]);

                    //erosionAmount = deltaT*erosionRate*(streamPower[i]-rockResistivity[i]);
                    //erosionAmount = deltaT*erosionRate*streamPower[i]*streamPower[i]/(1+rockResistivity[i]);
                    
                    //erosionAmount = deltaT*erosionRate*streamPower[i]/(1+rockResistivity[i]);
                    //erosionAmount = deltaT*erosionRate*streamPower[i];
                    
                    //erosionAmount = deltaT*erosionRate*(streamPower[i]/rockResistivity[i]-1);
                    //erosionAmount = deltaT*erosionRate*(streamPower[i]-rockResistivity[i]);
                    erosionAmount = deltaT*erosionRate*streamPower[i];
                }else{
                    erosionAmount = deltaT*erosionRate*minErosionRate;
                }

                if (erosionAmount > dHMax)
                {
                    erosionAmount = dHMax;
                }

                rock[i] = rock[i] - erosionAmount;
                sediment[i] = sediment[i] + expansionFactor * erosionAmount;
            }

            __kernel void ThermalErosion(float deltaT, float thermalErosionRate, float sedimentLimit, float expansionFactor, float talusSlope,
            __global float * rock, __global float * sediment, __global float * water, __global float * slope, __global float * rockResistivity)
            {
                //
                // Rock -> sediment 
                // Erosion speed is increased by slope, and is only performed when sediment is below a limit.
                //
                int i = get_global_id(0);

                if (sediment[i] < sedimentLimit && water[i] < sedimentLimit && slope[i] > talusSlope){
                    //float erosionAmount = 0.02*(slope[i]-talusSlope)*deltaT*thermalErosionRate;
                    // The rock resistivity factor makes the rock harder (less erodable) in certain regions.
                    float erosionAmount = 0.02*(slope[i]-talusSlope)*deltaT*thermalErosionRate/(1+rockResistivity[i]);
                    
                    //float erosionAmount = 0.02*deltaT*thermalErosionRate;
                    rock[i] = rock[i] - erosionAmount;
                    sediment[i] = sediment[i] + expansionFactor * erosionAmount;
                }
            }

            __kernel void SedimentSlippageCalculation(float deltaT, float slippageRate, float talusAngle, float triangleLength, float minRadius, 
            __global int * jTarget, __global int * kTarget, __global int * lTarget, 
            __global int * j, __global int * k, __global int * l, 
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *slope)
            {
                int i = get_global_id(0);

                float dHj = rock[i] + sediment[i] - rock[j[i]] - sediment[j[i]];
                float dHk = rock[i] + sediment[i] - rock[k[i]] - sediment[k[i]];
                float dHl = rock[i] + sediment[i] - rock[l[i]] - sediment[l[i]];

                float slopej = atan((0.00001+dHj)/(triangleLength * (minRadius+rock[i]+sediment[i])));
                float slopek = atan((0.00001+dHk)/(triangleLength * (minRadius+rock[i]+sediment[i])));
                float slopel = atan((0.00001+dHl)/(triangleLength * (minRadius+rock[i]+sediment[i])));

                float fj = 0.0;
                float fk = 0.0;
                float fl = 0.0;

                //if (slopej > talusAngle){
                //    fj = deltaT * slippageRate * (dHj - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //}
                //if (slopek > talusAngle){
                //    fk = deltaT * slippageRate * (dHk - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //}
                //if (slopel > talusAngle){
                //    fl = deltaT * slippageRate * (dHl - triangleLength * (minRadius+rock[i]+sediment[i]) * tan(talusAngle));
                //} 


                if (slope[i]>talusAngle)
                {
                    if (dHj > 0)
                    {
                        fj = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fj>dHj){fj = dHj;}
                    }
                    if (dHk > 0)
                    {
                        fk = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fk>dHk){fk = dHk;}
                    }
                    if (dHl > 0)
                    {
                        fl = deltaT * slippageRate * (slope[i]-talusAngle);
                        if (fl>dHl){fl = dHl;}
                    }
                }

                float scalingParameter = 0.5*sediment[i]/(deltaT*(fj + fk + fl + 0.0001));
                if (scalingParameter > 1){
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

            __kernel void SedimentSlippageUpdate(float deltaT,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *height)
            {
              int i = get_global_id(0);

              height[i] = height[i] + deltaT*(flowInj[i] + flowInk[i] + flowInl[i] - flowOut[i]);
            }

            __kernel void SedimentFlow(float deltaT, float flowRate, float sedimentResistivity,
            __global int *jTarget, __global int *kTarget, __global int *lTarget,
            __global int *j, __global int *k, __global int *l,
            __global float *waterFlowj, __global float *waterFlowk, __global float *waterFlowl,
            __global float * flowInj, __global float * flowInk, __global float * flowInl, __global float * flowOut,
            __global float *rock, __global float *sediment, __global float *slope, __global float *streamPower)
            {
              int i = get_global_id(0);

              float sedimentFlowFactor = flowRate * streamPower[i];
              //float sedimentFlowFactor = flowRate;
              //float sedimentFlowFactor = 0.0;
              //if (streamPower[i]>sedimentResistivity){
              //  //sedimentFlowFactor = flowRate * (streamPower[i]/sedimentResistivity-1);
              //  sedimentFlowFactor = flowRate * (streamPower[i]-sedimentResistivity);
              //} else {
              //  sedimentFlowFactor = 0.0;
              //}

              float dHj = rock[i] + sediment[i] - rock[j[i]] - sediment[j[i]];
              float dHk = rock[i] + sediment[i] - rock[k[i]] - sediment[k[i]];
              float dHl = rock[i] + sediment[i] - rock[l[i]] - sediment[l[i]];

              // The 0.95 acts as a drag coefficient. It limits the amount of noise and makes oceans calmer.
              float fj = sedimentFlowFactor * waterFlowj[i];
              //float fj = deltaT*sedimentFlowFactor * dHj;
              if (fj<0){  
              fj = 0;  
              }  

              float fk = sedimentFlowFactor * waterFlowk[i];
              //float fk = deltaT*sedimentFlowFactor * dHk;
              if (fk<0){  
              fk = 0;  
              }  

              float fl = sedimentFlowFactor * waterFlowl[i];
              //float fl = deltaT*sedimentFlowFactor * dHl;
              if (fl<0){
              fl = 0;
              }
              
              float slopeFactor;
              slopeFactor = (0+100*slope[i]);
              //slopeFactor = (0+1000*slope[i]*slope[i]);
              //if (slope[i]<0.1)
              //{
              //  slopeFactor = (0+20*slope[i]);
              //}else
              //{
              //  slopeFactor = 1000.0;
              //}
              
              // This can be used to limit the sediment flow on plat planes/oceans. This reduces lag which may occur.
              //if (fj > slopeFactor*dHj)
              //{
              //  fj = slopeFactor*dHj;
              //}
              //if (fk > slopeFactor*dHk)
              //{
              //  fk = slopeFactor*dHk;
              //}
              //if (fl > slopeFactor*dHl)
              //{
              //  fl = slopeFactor*dHl;
              //}

              if (dHj < 0.0){
                fj = 0.0;
              }
              if (dHk < 0.0){
                fk = 0.0;
              }
              if (dHl < 0.0){
                fl = 0.0;
              }

              float scalingParameter = 0.5*sediment[i]/(deltaT*(fj + fk + fl + 0.0001));
              if (scalingParameter > 1.0){
                scalingParameter = 1.0;
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

            __kernel void UpdateVertices(int nVertices, float minRadius,
            __global int * facesConnectingToVertex, __global float * unscaledVertices,
            __global float * sedimentVertices, __global float * waterVertices,
            __global float * rock, __global float * sediment, __global float * water)
            {
                int i = get_global_id(0);

                float sedimentRadius = 0.0;
                float waterRadius = 0.0;
                for (int iFace = 0; iFace < 6; iFace++)
                {
                    sedimentRadius += rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]];
                    waterRadius += rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]] + water[facesConnectingToVertex[iFace + i*6]];
                }
                sedimentRadius /= 6.0;
                sedimentRadius += minRadius;
                waterRadius /= 6.0;
                waterRadius += minRadius;

                for (int iDimension = 0; iDimension < 3; iDimension++)
                {
                    sedimentVertices[iDimension + i*3] = sedimentRadius * unscaledVertices[iDimension + i*3];
                    waterVertices[iDimension + i*3] = waterRadius * unscaledVertices[iDimension + i*3];
                }
            }

            __kernel void UpdateVisualizationVertices(int nVertices, float minRadius, float sedimentOffset, float waterOffset,
            __global int * facesConnectingToVertex, __global float * unscaledVertices,
            __global float * rockVertices, __global float * sedimentVertices, __global float * waterVertices,
            __global float * rock, __global float * sediment, __global float * water)
            {
                int i = get_global_id(0);

                float rockRadius = 0.0;
                float sedimentRadius = 0.0;
                float waterRadius = 0.0;
                for (int iFace = 0; iFace < 6; iFace++)
                {
                    rockRadius += rock[facesConnectingToVertex[iFace + i*6]];

                    float sedimentRadiusTmp = rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]];
                    if (sedimentRadiusTmp - sedimentOffset < rockRadius)
                    {
                        sedimentRadiusTmp -= sedimentOffset;
                    }
                    sedimentRadius += sedimentRadiusTmp;

                    float waterRadiusTmp = rock[facesConnectingToVertex[iFace + i*6]] + sediment[facesConnectingToVertex[iFace + i*6]] + water[facesConnectingToVertex[iFace + i*6]];
                    if (waterRadiusTmp - waterOffset < rockRadius || waterRadiusTmp - waterOffset < sedimentRadius)
                    {
                        waterRadiusTmp -= waterOffset;
                    }
                    waterRadius += waterRadiusTmp;
                }
                rockRadius /= 6.0;
                sedimentRadius /= 6.0;
                waterRadius /= 6.0;
                
                //if (sedimentRadius - sedimentOffset < rockRadius)
                //{
                //    sedimentRadius -= sedimentOffset/6;
                //}
                //if (waterRadius - waterOffset < rockRadius || waterRadius - waterOffset < sedimentRadius)
                //{
                //    waterRadius -= waterOffset;
                //}
                
                rockRadius += minRadius;
                sedimentRadius += minRadius;
                waterRadius += minRadius;

                for (int iDimension = 0; iDimension < 3; iDimension++)
                {
                    rockVertices[iDimension + i*3] = rockRadius * unscaledVertices[iDimension + i*3];
                    sedimentVertices[iDimension + i*3] = sedimentRadius * unscaledVertices[iDimension + i*3];
                    waterVertices[iDimension + i*3] = waterRadius * unscaledVertices[iDimension + i*3];
                }
            }
            """).build()

class Visualizer():
    def __init__(self, world, sedimentOffset, waterOffset, rockHeight, sedimentHeight, waterHeight, sedimentMaxDepth=1, waterMaxDepth=1):
        # Sets up lists needed to update the triangle vertices.
        kdTree = cKDTree(world.unscaledFaceCoordinates)
        rTypical, i = kdTree.query(world.unscaledVertices[0, :])
        rQuery, queryResult = kdTree.query(world.unscaledVertices[:, :], k=6)
        self.queryResult = np.array(queryResult)

        self.world = world
        self.sedimentOffset = sedimentOffset
        self.waterOffset = waterOffset
        self.sedimentMaxDepth = sedimentMaxDepth
        self.waterMaxDepth = waterMaxDepth
        # Sets up animation
        self.rockVertices = self.world.unscaledVertices.copy()
        self.sedimentVertices = self.world.unscaledVertices.copy()
        self.waterVertices = self.world.unscaledVertices.copy()



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
        r = self.world.minRadius + np.sum(rSediment[:, :, 0] + rWater[:, :, 0], axis=1) / 6 + - self.waterOffset
        self.waterVertices[:, 0] = r * self.world.unscaledVertices[:, 0]
        self.waterVertices[:, 1] = r * self.world.unscaledVertices[:, 1]
        self.waterVertices[:, 2] = r * self.world.unscaledVertices[:, 2]

        self.rockMesh = pv.PolyData(self.rockVertices, np.hstack(self.world.f))
        self.sedimentMesh = pv.PolyData(self.sedimentVertices, np.hstack(self.world.f))
        self.waterMesh = pv.PolyData(self.waterVertices, np.hstack(self.world.f))

        self.plotter = pv.Plotter()
        self.plotter.add_mesh(self.rockMesh, smooth_shading=False, color=(0.2, 0.15, 0.15, 1))
        self.plotter.add_mesh(self.sedimentMesh, smooth_shading=False, color=(0.35, 0.3, 0.25, 1))

        from matplotlib.colors import ListedColormap
        waterMapping = np.linspace(self.waterMaxDepth, 0, 256)
        newcolorsWater = np.zeros((256, 4))
        for i, mapValue in enumerate(waterMapping):
            newcolorsWater[waterMapping < mapValue] = np.array([0.1, 0.5 - 0.4 * i / 256, 0.7 - 0.4 * i / 256, 1])
        waterColormap = ListedColormap(newcolorsWater)

        self.waterMesh.add_field_array(scalars=waterHeight, name='water_depth')
        #self.plotter.add_mesh(self.waterMesh, scalars='water_depth', smooth_shading=False, cmap=waterColormap, clim=[0, waterMaxDepth])
        self.plotter.add_mesh(self.waterMesh, smooth_shading=False, color=(0.15, 0.2, 0.35))


        #self.plotter.enable_eye_dome_lighting()
        self.plotter.show(auto_close=False)

    def Update(self, rockHeight, sedimentHeight, waterHeight, erosion):
        # Uses face height values to calculate the vertex positions, on the GPU.
        #erosion.kernel.kernels.UpdateVisualizationVertices(erosion.kernel.queue, erosion.facesConnectingToVertex[:, 0].shape, None, erosion.nVertices, erosion.minRadius,
        #                                                np.array(self.sedimentOffset).astype(np.float32), np.array(self.waterOffset).astype(np.float32),
        #                                                erosion.facesConnectingToVertex_buf, erosion.unscaledVertices_buf,
        #                                                erosion.rockVertices_buf, erosion.sedimentVertices_buf, erosion.waterVertices_buf,
        #                                                erosion.terrainHeight_buf, erosion.sedimentHeight_buf, erosion.waterHeight_buf)
        erosion.kernel.kernels.UpdateVisualizationVertices(erosion.kernel.queue, erosion.facesConnectingToVertex[:, 0].shape, None, erosion.nVertices, erosion.minRadius,
                                                        np.array(self.sedimentOffset).astype(np.float32), np.array(self.waterOffset).astype(np.float32),
                                                        erosion.facesConnectingToVertex_buf, erosion.unscaledVertices_buf,
                                                        erosion.rockVertices_buf, erosion.sedimentVertices_buf, erosion.waterVertices_buf,
                                                        erosion.terrainHeight_buf, erosion.sedimentHeight_buf, erosion.waterHeight_buf)
        cl.enqueue_copy(erosion.kernel.queue, erosion.rockVertices, erosion.rockVertices_buf)
        cl.enqueue_copy(erosion.kernel.queue, erosion.sedimentVertices, erosion.sedimentVertices_buf)
        cl.enqueue_copy(erosion.kernel.queue, erosion.waterVertices, erosion.waterVertices_buf)

        self.rockVertices = erosion.rockVertices
        self.sedimentVertices = erosion.sedimentVertices
        self.waterVertices = erosion.waterVertices


        # plotter.update_scalars(slope, mesh=terrainMesh, render=False)
        #self.plotter.update_scalars(erosion.streamPower, mesh=self.waterMesh, render=False)
        #self.plotter.update_scalars(erosion.velocity, mesh=self.waterMesh, render=False)
        #self.plotter.update_scalars(erosion.waterSlope, mesh=self.waterMesh, render=False)

        waterH = erosion.waterHeight[:, 0]# - self.waterOffset
        self.waterMesh['water_depth'] = waterH

        #self.plotter.update_scalars(sedimentH, mesh=self.sedimentMesh, render=False)
        #self.plotter.update_scalars(erosion.waterHeight[:, 0]/self.waterOffset, mesh=self.waterMesh, render=False)
        self.plotter.update_coordinates(points=self.rockVertices, mesh=self.rockMesh, render=False)
        self.plotter.update_coordinates(points=self.sedimentVertices, mesh=self.sedimentMesh, render=False)
        self.plotter.update_coordinates(points=self.waterVertices, mesh=self.waterMesh, render=False)

        self.rockMesh.compute_normals(point_normals=True, inplace=True)
        self.sedimentMesh.compute_normals(point_normals=True, inplace=True)
        self.waterMesh.compute_normals(point_normals=True, inplace=True)
        self.plotter.render()

class SaveClass():
    def __init__(self, world, rock, sediment, water):
        self.world = world
        self.rock = rock
        self.sediment = sediment
        self.water = water

class Erosion():
    def __init__(self,
                 rock,
                 sediment,
                 water,
                 world,
                 kernel,
                 deltaT=0.03,
                 waterFlowSpeed = 100,
                 waterFlowFriction = 0.98,
                 sedimentErosionLimit = 1,
                 thermalErosionRate = 1,
                 rockToSedimentExpansion = 1,
                 streamPowerMultiplier = 10,
                 rockResistivity = 5,
                 sedimentResistivity = 2,
                 hydraulicErosionRate = 1,
                 minHydrolicErosionRate = 0.01,
                 sedimentFlowSpeed = 10,
                 sedimentSlippageRate = 20,
                 talusAngle = 30*np.pi/180,
                 evaporationRate=0.05,
                 rainAmount=1):
        self.world = world
        self.kernel = kernel

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

        triangleLength = np.array(4 * np.sqrt(np.pi) / np.sqrt(3 * np.sqrt(3) * np.size(world.f, 0)))
        self.triangleLength = triangleLength.astype(np.float32)

        sqrt3_2 = np.array(np.sqrt(3) / 2)
        self.sqrt3_2 = sqrt3_2.astype(np.float32)

        self.streamPowerParameter = np.array(streamPowerMultiplier).astype(np.float32)
        self.sedimentResistivity = np.array(sedimentResistivity).astype(np.float32)

        carryCapacityParameter = np.array(0.1)
        carryCapacityParameter = carryCapacityParameter.astype(np.float32)

        self.erosionRate = np.array(hydraulicErosionRate).astype(np.float32)
        self.minErosionRate = np.array(minHydrolicErosionRate).astype(np.float32)
        depositionRate = np.array(0.1)
        depositionRate = depositionRate.astype(np.float32)

        self.sedimentFlowParameter = np.array(sedimentFlowSpeed).astype(np.float32)

        self.slippageParameter = np.array(sedimentSlippageRate).astype(np.float32)
        self.talusAngle = np.array(talusAngle).astype(np.float32)

        self.evaporationRate = evaporationRate
        self.rainAmount = rainAmount

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
        self.nVertices = np.array(np.size(world.unscaledVertices, 0)).astype(np.int)


        jTarget = faceConnectionsIndices[:, 0].astype(np.int)
        kTarget = faceConnectionsIndices[:, 1].astype(np.int)
        lTarget = faceConnectionsIndices[:, 2].astype(np.int)

        j = world.faceConnections[:, 0]
        k = world.faceConnections[:, 1]
        l = world.faceConnections[:, 2]
        j = j.astype(np.int)
        k = k.astype(np.int)
        l = l.astype(np.int)

        #waterHeight = np.zeros_like(world.faceRadius, dtype=np.float32)
        #sedimentHeight = np.zeros_like(world.faceRadius, dtype=np.float32)
        heightUpdated = world.faceRadius - np.min(world.faceRadius)
        heightUpdated = heightUpdated.astype(np.float32)
        # heightUpdated = np.zeros_like(world.faceRadius, dtype=

        self.velocity = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.slope = np.zeros_like(world.faceRadius, dtype=np.float32)
        self.waterSlope = np.zeros_like(world.faceRadius, dtype=np.float32)
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
        self.waterFlowj_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowj)
        self.waterFlowk_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowk)
        self.waterFlowl_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowl)
        self.waterFlowUpdatedj_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)
        self.waterFlowUpdatedk_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)
        self.waterFlowUpdatedl_buf = cl.Buffer(kernel.ctx, self.kernel.mf.WRITE_ONLY, heightUpdated.nbytes)

        self.rockResistivity = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,hostbuf=rockResistivity.astype(np.float32))
        self.terrainHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.rockHeight)
        self.waterHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterHeight)
        self.sedimentHeight_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.sedimentHeight)
        self.heightUpdated_buf = cl.Buffer(kernel.ctx, self.kernel.mf.READ_WRITE, heightUpdated.nbytes)
        #-------------------------------------------------------------------------------------------------------------




        self.heightUpdated = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowUpdatedj = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowUpdatedk = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowUpdatedl = np.zeros_like(self.world.faceRadius, dtype=np.float32)

        self.waterFlowInj = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowInk = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowInl = np.zeros_like(self.world.faceRadius, dtype=np.float32)
        self.waterFlowOut = np.zeros_like(self.world.faceRadius, dtype=np.float32)

        self.waterFlowUpdatedj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE,
                                               self.waterFlowUpdatedj.nbytes)
        self.waterFlowUpdatedk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE,
                                               self.waterFlowUpdatedk.nbytes)
        self.waterFlowUpdatedl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE,
                                               self.waterFlowUpdatedl.nbytes)

        self.waterFlowInj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInj.nbytes)
        self.waterFlowInk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInk.nbytes)
        self.waterFlowInl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInl.nbytes)
        self.waterFlowOut_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.WRITE_ONLY, self.waterFlowOut.nbytes)
        self.sedimentFlowInj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInj.nbytes)
        self.sedimentFlowInk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInk.nbytes)
        self.sedimentFlowInl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.waterFlowInl.nbytes)
        self.sedimentFlowOut_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.WRITE_ONLY, self.waterFlowOut.nbytes)


        self.heightUpdated_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.heightUpdated.nbytes)
        self.velocity_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.velocity.nbytes)
        self.slope_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.slope.nbytes)
        self.waterSlope_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.slope.nbytes)
        self.streamPower_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_WRITE, self.slope.nbytes)

    def Run(self, nIterations):
        nIterations = nIterations

        for i in range(nIterations):
            rainAmount = self.rainAmount
            self.waterHeight[:, 0] += self.deltaT * rainAmount

            self.terrainHeight_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,
                                               hostbuf=self.rockHeight)
            self.waterHeight_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR,
                                             hostbuf=self.waterHeight)

            self.waterFlowj_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowj)
            self.waterFlowk_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowk)
            self.waterFlowl_buf = cl.Buffer(self.kernel.ctx, self.kernel.mf.READ_ONLY | self.kernel.mf.COPY_HOST_PTR, hostbuf=self.waterFlowl)



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

            # Evaporation
            self.waterHeight *= (1 - self.evaporationRate * self.deltaT)

            print(np.min(self.streamPower))
            print(np.max(self.streamPower))
            print(np.mean(self.streamPower))
            print(' ')

def InitializeEarth(world):
    faceCoordinatesNormalized = world.faceCoordinates.copy()
    faceCoordinatesNormalized[:, 0] /= world.faceRadius
    faceCoordinatesNormalized[:, 1] /= world.faceRadius
    faceCoordinatesNormalized[:, 2] /= world.faceRadius
    cutOffHeight = 6
    #seed = np.random.randint(0, 100)
    #rockHeight = 6 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.4) ** 3 + \
    #             2 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6) ** 3 + \
    #             1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=1.8) + \
    #             3 * (1 - 2 * np.abs(world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.4) - 0.5)) ** 2
    #rockHeight = 3 * (1 - 2 * np.abs(world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.4) - 0.5)) ** 2
    #rockHeight = 8 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6) ** 2
    rockHeight = 8 * world.WarpedPerlinNoise(faceCoordinatesNormalized,
                                             xWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                             yWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                             zWarp=0.5*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                             octaves=15, persistence=0.6) + \
                 6 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.2
                                       )
    rockHeight = 10 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.4)
    continentPerlin = 1 * world.WarpedPerlinNoise(faceCoordinatesNormalized,
                                             xWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             yWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             zWarp=2*world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6),
                                             octaves=15, persistence=0.1)

    #continentPerlin = 1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6)
    #continentPerlin = 10 * np.sin(continentPerlin * np.pi / 2)

    #continentPerlin = 1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6)
    #continentPerlin = 10 * (np.sin(continentPerlin * np.pi / 2) + 0.5) ** 2

    #continentPerlin = 1 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.6)
    continentPerlin = np.sin(continentPerlin*np.pi/2)**2
    continentPerlinTmp = continentPerlin.copy()
    continentPerlinTmp -= 0.5
    continentPerlin[continentPerlinTmp<0] = 0.5
    continentPerlin[continentPerlinTmp>0] = 0
    continentPerlin *= 1
    rockHeight *= 3
    #rockHeight[continentPerlin == 0] = 0
    #rockHeight *= continentPerlin# + 10*(0.5-continentPerlinTmp)**4

        #5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.9) ** 5 + \
    #rockHeight -= cutOffHeight
    #rockHeight[rockHeight < 0] = 0
    #rockHeight[rockHeight > 0] = 3

    sedimentHeight = 0*rockHeight.copy()
    waterHeight = 0*rockHeight.copy()
    rockHeight = rockHeight.astype(np.float32)
    sedimentHeight = sedimentHeight.astype(np.float32)
    waterHeight = waterHeight.astype(np.float32)
    return [rockHeight, sedimentHeight, waterHeight]

def Main():
    nDivisions = 100

    #rockResistivitySpan = [0.5, 3.5]
    rockResistivitySpan = [3.5, 10.5]


    fileToOpen = 'world_template_' + str(nDivisions) + '.pkl'
    try:
        world = pickle.load(open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "rb"))
    except:
        world = World.SphericalWorld(nDivisions=nDivisions)
        pickle.dump(world, open(Root_Directory.Path() + '/Data/Cached_Worlds/' + fileToOpen, "wb"))

    # world = World.SphericalWorld(nDivisions=nDivisions)

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

    kernels = OpenclKernel(mode=2)
    print('kernels initialized')

    [terrainHeight, sedimentHeight, waterHeight] = InitializeEarth(world=world)
    rockResistivity = rockResistivitySpan[0] + (rockResistivitySpan[1]-rockResistivitySpan[0])*world.WarpedPerlinNoise(faceCoordinatesNormalized,
                                   xWarp=0.5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                   yWarp=0.5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                   zWarp=0.5 * world.PerlinNoise(faceCoordinatesNormalized, octaves=15, persistence=0.3),
                                   octaves=15, persistence=0.5, scale=1)**1
    #terrainHeight = 50*rockResistivity
    print('Heights initialized')

    visualizer = Visualizer(world=world, sedimentOffset=0.1, waterOffset=0.2, rockHeight=terrainHeight,
                            sedimentHeight=sedimentHeight, waterHeight=waterHeight, waterMaxDepth=1) # 0.3
    print('Visualizer initialized')

    erosion = Erosion(rock=terrainHeight,
                      sediment=sedimentHeight,
                      water=waterHeight,
                      world=world,
                      kernel=kernels,
                      deltaT=0.05,#0.01
                      waterFlowSpeed=100,#100
                      waterFlowFriction=1.0,#0.95
                      sedimentErosionLimit=1,
                      thermalErosionRate=0,#10
                      rockToSedimentExpansion=1,
                      streamPowerMultiplier=3000,
                      rockResistivity=rockResistivity,
                      sedimentResistivity=0.5,
                      hydraulicErosionRate=0, #0.01
                      minHydrolicErosionRate = 0.000001,
                      sedimentFlowSpeed=1,#1
                      sedimentSlippageRate=0,
                      talusAngle=30 * np.pi / 180,
                      evaporationRate=0,#0.15
                      rainAmount=0.0001)#0.05
    #erosion.Run(nIterations=200)
    #visualizer.Update(rockHeight=terrainHeight, sedimentHeight=sedimentHeight, waterHeight=waterHeight, erosion=erosion)

    '''
    erosion = Erosion(rock=erosion.rockHeight,
                      sediment=erosion.sedimentHeight,
                      water=erosion.waterHeight,
                      world=world,
                      kernel=kernels,
                      deltaT=0.01,#0.01
                      waterFlowSpeed=10,#100
                      waterFlowFriction=1.0,#0.95
                      sedimentErosionLimit=1,
                      thermalErosionRate=0,#10
                      rockToSedimentExpansion=1,
                      streamPowerMultiplier=15,
                      rockResistivity=0.1,
                      sedimentResistivity=0.01,
                      hydraulicErosionRate=0.1, #0.01
                      minHydrolicErosionRate = 0.00001,
                      sedimentFlowSpeed=10,#1
                      sedimentSlippageRate=1000,
                      talusAngle=30 * np.pi / 180,
                      evaporationRate=0.05,#0.15
                      rainAmount=0.005)#0.05
    '''
    erosion = Erosion(rock=erosion.rockHeight,
                      sediment=erosion.sedimentHeight,
                      water=erosion.waterHeight,
                      world=world,
                      kernel=kernels,
                      deltaT=0.01,#0.01
                      waterFlowSpeed=1000,#100
                      waterFlowFriction=1.0,#0.95
                      sedimentErosionLimit=0.1,
                      thermalErosionRate=100,#10
                      rockToSedimentExpansion=1,
                      streamPowerMultiplier=15*8,
                      rockResistivity=rockResistivity,
                      sedimentResistivity=0.001,
                      hydraulicErosionRate=0.1, #1
                      minHydrolicErosionRate = 0.001,
                      sedimentFlowSpeed=100,#100
                      sedimentSlippageRate=1000,
                      talusAngle=30 * np.pi / 180,
                      evaporationRate=0.05,#0.15
                      rainAmount=0.01/8)#0.05
    print('Erosion initialized')

    print('TOTAL LANDMASS BEFORE SIMULATION', np.sum(erosion.rockHeight+erosion.sedimentHeight))

    #erosion.rainAmount = 0
    #erosion.waterHeight +=0.1

    ticTotalSimulation = time.time()
    for i in range(2000):
        erosion.Run(nIterations=1)
        #erosion.rockHeight[sedimentHeight<0.1] += 0.0001
        if i == 1100:
            #erosion.flowParameter = np.array(10).astype(np.float32)
            #erosion.frictionParameter = np.array(0.98).astype(np.float32)
            erosion.rainAmount = 0
            erosion.evaporationRate = 0
            #erosion.erosionRate = np.array(0).astype(np.float32)
            #erosion.sedimentFlowParameter = np.array(0).astype(np.float32)
            #erosion.thermalErosionRate = np.array(0).astype(np.float32)
            print('-------------------')
            print('   RAIN STOPPED')
            print('-------------------')
        if (i+1)%200 == 0 and i<1100 and False:
            print('Tectonic shift')
            #seed = np.random.randint(0, 100)
            #print(seed)
            tectonicUpshift = 5*world.PerlinNoise(faceCoordinatesNormalized, octaves=10, persistence=0.7)
            tectonicUpshift -= np.mean(tectonicUpshift)
            #tectonicUpshift -= 10
            #tectonicUpshift[tectonicUpshift<0] = 0
            #tectonicUpshift[tectonicUpshift>0] = 10

            erosion.rockHeight += tectonicUpshift

            #erosion.waterHeight *= 0.5
            #erosion.rockHeight += 0.5*erosion.sedimentHeight
            #erosion.sedimentHeight /= erosion.sedimentHeight

        if i%10 == 0 and False:
            visualizer.Update(rockHeight=terrainHeight, sedimentHeight=sedimentHeight, waterHeight=waterHeight,erosion=erosion)

    #erosion.rainAmount = 0
    #erosion.evaporationRate = 0.1
    #erosion.Run(nIterations=500)
    tocTotalSimulation = time.time()
    print('Total simulation time : ', tocTotalSimulation - ticTotalSimulation)

    print('TOTAL LANDMASS AFTER SIMULATION', np.sum(erosion.rockHeight + erosion.sedimentHeight))

    visualizer.Update(rockHeight=terrainHeight, sedimentHeight=sedimentHeight, waterHeight=waterHeight, erosion=erosion)

    print('Rock Amount =     ', np.sum(erosion.rockHeight))
    print('Sediment Amount = ', np.sum(erosion.sedimentHeight))
    print('Water Amount =    ', np.sum(erosion.waterHeight))

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

Main()
#VisualizeLoadedWorld(fileToOpen='04')




