# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:24:47 2015

@author: fsc
"""



import sys
import numpy as np
 #   from PlaneParameters import * #Network properties.
from Branch3D import *
from random import shuffle
from mesh import Mesh





def Fractal_Tree_3D(param):
    #Read Mesh
    m=Mesh(param.meshfile)
    #Define the initial direction
    init_dir=(param.second_node-param.init_node)/np.linalg.norm(param.second_node-param.init_node)
    
    #Initialize the nodes object, contains the nodes and all the distance functions
    nodes=Nodes(param.init_node)
    #Project the first node to the mesh.
    point,tri=m.project_new_point(nodes.nodes[0])
    if tri>=0:
        init_tri=tri
    else:
        print 'initial point not in mesh'
        sys.exit(0)
    #Initialize the dictionary that stores the branches objects
    branches={}
    last_branch=0
    #Compute the first branch
    branches[last_branch]=Branch(m,0,init_dir,init_tri,param.init_length,0.0,0.0,nodes,[0],int(param.init_length/param.l_segment))
    branches_to_grow=[]
    branches_to_grow.append(last_branch)
    
    
    ien=[]
    for i_n in range(len(branches[last_branch].nodes)-1):
        ien.append([branches[last_branch].nodes[i_n],branches[last_branch].nodes[i_n+1]]) 
    #To grow fascicles 
    if param.Fascicles:
        brother_nodes=[]    
        brother_nodes+=branches[0].nodes    
        for i_branch in range(len(param.fascicles_angles)):
            last_branch+=1
            angle=param.fascicles_angles[i_branch]
            branches[last_branch]=Branch(m,branches[0].nodes[-1],branches[0].dir,branches[0].tri,param.fascicles_length[i_branch],angle,0.0,nodes,brother_nodes,int(param.fascicles_length[i_branch]/param.l_segment))
            brother_nodes+=branches[last_branch].nodes 
            
            for i_n in range(len(branches[last_branch].nodes)-1):
                ien.append([branches[last_branch].nodes[i_n],branches[last_branch].nodes[i_n+1]])                 
        branches_to_grow=[1,2]

        
    for i in range(param.N_it):
        shuffle(branches_to_grow)
        new_branches_to_grow=[]
        angle=-param.branch_angle*np.random.choice([-1,1])
        for g in branches_to_grow:
            for j in range(2):
                brother_nodes=[]
                brother_nodes+=branches[g].nodes
                if j>0:
                    brother_nodes+=branches[last_branch].nodes
                
                #Add new branch
                last_branch+=1
                print last_branch
                l=param.length#+np.random.normal(0,np.sqrt(0.2*param.length))
                branches[last_branch]=Branch(m,branches[g].nodes[-1],branches[g].dir,branches[g].tri,l,angle,param.w,nodes,brother_nodes,int(param.length/param.l_segment))
                #Add nodes to IEN
                for i_n in range(len(branches[last_branch].nodes)-1):
                    ien.append([branches[last_branch].nodes[i_n],branches[last_branch].nodes[i_n+1]]) 

                #Add to the new array
                if branches[last_branch].growing:
                    new_branches_to_grow.append(last_branch)
                
                branches[g].child[j]=last_branch
                angle=-angle                
        branches_to_grow=new_branches_to_grow
        
    if param.save:
        from tvtk.api import tvtk
        print 'Finished growing, writing paraview file'
        line_type = tvtk.Line().cell_type
        xyz=np.zeros((len(nodes.nodes),3))
        for i in range(len(nodes.nodes)):
            xyz[i,:]=nodes.nodes[i]
        ug = tvtk.UnstructuredGrid(points=xyz)
        ug.set_cells(line_type, ien)
        
        w = tvtk.XMLUnstructuredGridWriter(input = ug, file_name=(param.filename+'.vtu'))
        
        w.write()
        
        np.savetxt(param.filename+'_ien.txt',ien,fmt='%d')
        np.savetxt(param.filename+'_xyz.txt',xyz)
        np.savetxt(param.filename+'_endnodes.txt',nodes.end_nodes,fmt='%d')
        

    return branches,nodes


from sphere_parameters import Parameters

param=Parameters()

branches, nodes = Fractal_Tree_3D(param)