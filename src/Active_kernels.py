#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kernels used to compute swimming velocity and cold induced mortality.
"""


from math import sqrt, cos, sin, atan2, exp, log
import math
from parcels import random



def compute_Mass(particle, fieldset, time):
    "Compute mass (kg). SCL is in meters."
    if particle.active == 1:
        particle.M = fieldset.a*(particle.SCL)**fieldset.b


def compute_Tmin_Topt(particle, fieldset, time): 
    if particle.active == 1:
        particle.Topt = fieldset.T0 - fieldset.to * sqrt(particle.M)
        particle.Tmin = fieldset.T0 - fieldset.tm * sqrt(particle.M)



def compute_PPmax_VGBF(particle, fieldset, time):
    """
    Compute food threshold.
    """
    if particle.active == 1:
        x = particle.SCL / fieldset.SCLmax
        PPnorm = fieldset.b * fieldset.beta_jones * (1 - x) * x**(fieldset.b-1) / (1 - x**(fieldset.b * fieldset.beta_jones))
        particle.PPmax = PPnorm * fieldset.P0
    

def compute_PPmax_Gompertz(particle, fieldset, time):
    """
    Assume F = c*M
    """
    if particle.active == 1:
        PPnorm = fieldset.c * particle.M
        particle.PPmax = PPnorm * fieldset.P0


def compute_vmax(particle, fieldset, time):
    """
    Compute maximum speed at current age.
    """
    if particle.active == 1:
        particle.vmax = fieldset.vscale*(particle.SCL**fieldset.d)



def compute_habitat(particle, fieldset, time):
    """
    Computes habitat at position, left, right, bottom and top.
    Computes habitat gradients.
    Save habT, habPP and hab at the particle location.
    Save xgradh and ygradh.
    Save T and NPP at particle location.
    """
    if particle.active == 1:
        #Convert dx to lon and lat
        dx_lon =  fieldset.grad_dx / (fieldset.deg * cos(particle.lat * math.pi / 180)) 
        dx_lat =  fieldset.grad_dx / fieldset.deg
        #
        #Get 5 T and 5 NPP
        #
        T0 = [fieldset.T[time, particle.depth, particle.lat, particle.lon],#position
               fieldset.T[time, particle.depth, particle.lat, particle.lon - dx_lon],#left
               fieldset.T[time, particle.depth, particle.lat, particle.lon + dx_lon],#right
               fieldset.T[time, particle.depth, particle.lat - dx_lat, particle.lon],#bottom
               fieldset.T[time, particle.depth, particle.lat + dx_lat, particle.lon]]#top
        
        NPP0 = [fieldset.NPP[time, particle.depth, particle.lat, particle.lon],#position
              fieldset.NPP[time, particle.depth, particle.lat, particle.lon - dx_lon],#left
              fieldset.NPP[time, particle.depth, particle.lat, particle.lon + dx_lon],#right
              fieldset.NPP[time, particle.depth, particle.lat - dx_lat, particle.lon],#bottom
              fieldset.NPP[time, particle.depth, particle.lat + dx_lat, particle.lon]]#top       
        #Save T and NPP at particle location
        particle.T = T0[0]
        particle.NPP = NPP0[0]
        #
        #Temperature habitat
        #
        Tmin = particle.Tmin
        Topt = particle.Topt
        T_hab = [0, 0, 0, 0, 0] #position, left, right, bottom and top
        #
        if T0[0] >= Topt:
            T_hab[0] = 1.0
        else:
            T_hab[0] = exp(-2*((T0[0]-Topt)/(Topt-Tmin))**2)
        #
        if T0[1] >= Topt:
            T_hab[1] = 1.0
        else:
            T_hab[1] = exp(-2*((T0[1]-Topt)/(Topt-Tmin))**2)
        #
        if T0[2] >= Topt:
            T_hab[2] = 1.0
        else:
            T_hab[2] = exp(-2*((T0[2]-Topt)/(Topt-Tmin))**2)
        #
        if T0[3] >= Topt:
            T_hab[3] = 1.0
        else:
            T_hab[3] = exp(-2*((T0[3]-Topt)/(Topt-Tmin))**2)
        #
        if T0[4] >= Topt:
            T_hab[4] = 1.0
        else:
            T_hab[4] = exp(-2*((T0[4]-Topt)/(Topt-Tmin))**2)
        #
        #Food habitat
        #
        food_hab = [0, 0, 0, 0, 0] #position, left, right, bottom and top
        #
        if NPP0[0] < 0:
            print('WARNING: negative NPP at lon,lat = %f,%f and time = %f: set to 0'%(particle.lon,particle.lat,time))
            food_hab[0] = 0
        else:
            food_hab[0] = min(NPP0[0]/particle.PPmax,1)
        #
        if NPP0[1] < 0:
            print('WARNING: negative NPP at lon,lat = %f,%f and time = %f: set to 0'%(particle.lon,particle.lat,time))
            food_hab[1] = 0
        else:
            food_hab[1] = min(NPP0[1]/particle.PPmax,1)
        #
        if NPP0[2] < 0:
            print('WARNING: negative NPP at lon,lat = %f,%f and time = %f: set to 0'%(particle.lon,particle.lat,time))
            food_hab[2] = 0
        else:
            food_hab[2] = min(NPP0[2]/particle.PPmax,1)
        #
        if NPP0[3] < 0:
            print('WARNING: negative NPP at lon,lat = %f,%f and time = %f: set to 0'%(particle.lon,particle.lat,time))
            food_hab[3] = 0
        else:
            food_hab[3] = min(NPP0[3]/particle.PPmax,1)
        #
        if NPP0[4] < 0:
            print('WARNING: negative NPP at lon,lat = %f,%f and time = %f: set to 0'%(particle.lon,particle.lat,time))
            food_hab[4] = 0
        else:
            food_hab[4] = min(NPP0[4]/particle.PPmax,1)
        #
        #Total habitat
        #
        particle.habT = T_hab[0]
        particle.habPP = food_hab[0]
        particle.hab = particle.habT * particle.habPP
        h_left = T_hab[1] * food_hab[1]
        h_right = T_hab[2] * food_hab[2]
        h_bot = T_hab[3] * food_hab[3]
        h_top = T_hab[4] * food_hab[4]
        #
        #Habitat gradient
        #
        particle.xgradh = (h_right - h_left)/(2 * fieldset.grad_dx)
        particle.ygradh = (h_top - h_bot)/(2 * fieldset.grad_dx)
        #
        #Safety check
        #
        if particle.hab < 0 or particle.hab > 1:
            print("Habitat is %f at lon,lat = %f,%f. Execution stops."%(particle.hab,particle.lon,particle.lat))
            exit(0)



def compute_swimming_direction(particle, fieldset, time):
    """
    Compute particule.theta
    Theta has to be between 0 and 2*pi for random.vommises, 0 corresponding to east.
    A tactic factor is used (t = [0,1]) as a memory effect (Benhamou 1991, Elementary orientation mechanisms).
    """
    if particle.active == 1:
        #Compute theta0
        theta0 = atan2(particle.ygradh,particle.xgradh) #return 0 in case xgradh=ygradh=0 (east !)
                                                        #but ok because vonmises becomes uniform without gradient
        if theta0 < 0:
            theta0 += 2 * math.pi # theta0 has to be between 0 and 2*pi for VonMises
        
        grad = sqrt(math.pow(particle.xgradh, 2) + math.pow(particle.ygradh, 2))
        
        #Compute theta
        prev_theta = particle.theta
        current_theta = random.vonmisesvariate(theta0,fieldset.alpha*grad)
        particle.theta = atan2((particle.t * sin(current_theta) + (1 - particle.t) * sin(prev_theta)) , (particle.t * cos(current_theta) + (1 - particle.t) * cos(prev_theta)))
        particle.t = fieldset.tactic_factor #re-initialize tactic factor in case particle beached
        #
        if particle.theta < 0:
            particle.theta += 2 * math.pi #theta0 has to be between 0 and 2*pi for VonMises



def compute_swimming_velocity(particle, fieldset, time):
    """
    Compute particule.u_swim and particle.v_swim
    """
    if particle.active == 1:
        particle.u_swim = particle.vmax * (1-particle.hab) * cos(particle.theta)
        particle.v_swim = particle.vmax * (1-particle.hab) * sin(particle.theta)
    

def compute_frenzy_speed(particle, fieldset, time):
    """
    Compute linear decrease of frenzy speed over days or constant speed.
    """
    if particle.active == 1 and particle.time < fieldset.frenzy_duration * 86400:
        if fieldset.frenzy_mode == 0:
            particle.frenzy_speed = fieldset.frenzy_speed
        elif fieldset.frenzy_mode == 1:
            particle.frenzy_speed = fieldset.frenzy_speed * (1 - particle.time / (fieldset.frenzy_duration * 86400))
        else:
            print("frenzy_mode not valid. Execution stops.")
            exit(0)


def swimming_frenzy(particle, fieldset, time):
    """
    Swim towards frenzy_theta (angle in rad defined with respect to east)
    during frenzy_duration days at a velocity of frenzy_speed m/s
    (define parameters in Species).
    This kernel overwrites previous u_swim and v_swim.
    """
    if particle.active == 1 and particle.time < fieldset.frenzy_duration * 86400:
        particle.u_swim = particle.frenzy_speed * cos(fieldset.frenzy_theta)
        particle.v_swim = particle.frenzy_speed * sin(fieldset.frenzy_theta)


def compute_wave_direction(particle, fieldset, time):
    """
    Compute wave direction based on Stokes drift (angle in rad with respect to east).
    In case Stokes Drift is 0 (i.e. on mask), return east (arbitrary direction !!!)
    """
    if particle.active == 1 and particle.time < fieldset.frenzy_duration * 86400:
        Us = fieldset.Ustokes[time, particle.depth, particle.lat, particle.lon]
        Vs = fieldset.Vstokes[time, particle.depth, particle.lat, particle.lon]
        
        if math.fabs(Us) < 1e-14 and math.fabs(Vs) < 1e-14: # On wave land mask
            particle.theta_wave = math.pi # Manual choice so that turtles swim eastward
        else:
            particle.theta_wave = atan2(Vs, Us)
            

def swim_against_waves(particle, fieldset, time):
    """
    Turtles swim at a velocity swimming_frenzy against wave direction
    during frenzy_duration days at a velocity of frenzy_speed m/s
    This kernel overwrites previous u_swim and v_swim.
    """
    if particle.active == 1 and particle.time < fieldset.frenzy_duration * 86400:
        particle.u_swim = -fieldset.frenzy_speed * cos(particle.theta_wave)
        particle.v_swim = -fieldset.frenzy_speed * sin(particle.theta_wave)


def cold_induced_mortality(particle, fieldset, time):
    """
    Increment particle.lethargy_time if T < Tmin.
    If particle.lethargy_time > cold_resistance, then delete particle.
    PB: how to keep in memory dead turtles ?
    """
    if particle.active == 1:
        if fieldset.T[time, particle.depth, particle.lat, particle.lon] < particle.Tmin:
            particle.lethargy_time += particle.dt
            if particle.lethargy_time > fieldset.cold_resistance:
                particle.cold_death = 1
                particle.active = 0
        else:
            particle.lethargy_time = 0

 
               








