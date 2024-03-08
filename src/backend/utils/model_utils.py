import torch
from model import GaussianModel
from tqdm import tqdm

def KDTree_clustering(points, num_leaf_nodes, starting_mask):
    assert points.shape[0] > num_leaf_nodes, "leaf_nodes must be smaller than the number of points"
    node_indices = [starting_mask]
    finished_nodes = []

    while len(node_indices)+len(finished_nodes) < num_leaf_nodes:
        node_idx = node_indices.pop(0)
        these_points = points[node_idx]
        dim_ranges = (these_points.amax(dim=0)-these_points.amin(dim=0))
        max_dim = torch.argmax(dim_ranges)

        center = torch.median(these_points[:,max_dim])
        mask = these_points[:,max_dim] < center
        left = node_idx[mask]
        right = node_idx[~mask]

        if(left.shape[0] > 1):
            node_indices.append(left)
        elif(left.shape[0] == 1):
            finished_nodes.append(left)
        if(right.shape[0] > 1):
            node_indices.append(right)
        elif(right.shape[0] == 1):
            finished_nodes.append(right)

    node_indices.extend(finished_nodes)

    return node_indices

def decimate_model(model : GaussianModel, pct = 100, selection_mask = None):
    assert model.get_num_gaussians == selection_mask.shape[0], "Selection mask size must equal number of gaussians in the model"
    
    points_xyz = model.get_xyz
    if(selection_mask is not None):         
        mask_indices = torch.argwhere(selection_mask)[:,0]
    else:
        mask_indices = torch.arange(model.get_num_gaussians, dtype=torch.long, device=model.get_xyz.device)
    num_points_final = int(selection_mask.sum() * (pct/100))
    
    tree_nodes = KDTree_clustering(points_xyz, num_points_final, mask_indices)
    new_xyz = []
    new_scales = []
    new_rots = []
    new_feats = []
    new_opacities = []
    for node in tree_nodes:
        avg_xyz = model.get_xyz[node].mean(dim=0)[None,:]
        avg_scale = model.scaling_inverse_activation(model.get_scaling[node].mean(dim=0) * (100/pct))[None,:]
        Q = model.get_rotation[node]
        # https://stackoverflow.com/questions/12374087/average-of-multiple-quaternions
        _, vecs = torch.linalg.eig(Q.T @ Q)
        avg_rot = torch.nn.functional.normalize(vecs[:,0:1].real).T
        avg_feat = model.get_features[node].mean(dim=0)[None,:,:]
        avg_opacity = model.inverse_opacity_activation(model.get_opacity[node].mean(dim=0))[None,:]

        new_xyz.append(avg_xyz)
        new_scales.append(avg_scale)
        new_rots.append(avg_rot)
        new_feats.append(avg_feat)
        new_opacities.append(avg_opacity)

    new_xyz = torch.cat(new_xyz, dim=0)    
    new_scales = torch.cat(new_scales, dim=0)
    new_rots = torch.cat(new_rots, dim=0)    
    new_feats = torch.cat(new_feats, dim=0)    
    new_opacities = torch.cat(new_opacities, dim=0)
    
    return new_xyz, new_scales, new_rots, new_feats, new_opacities
    
    