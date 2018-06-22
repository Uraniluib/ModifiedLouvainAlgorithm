# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 13:14:46 2018

@author: Jinglin
"""

#define class
# Structure sto_targetring a community 
class igraph_i_multilevel_community:
    size;           # Size of the community
    weight_inside;     # Sum of edge weights inside community 
    weight_all;        # Sum of edge weights starting/endingin the community 
    
class igraph_i_multilevel_community:
     size;             # Size of the community 
     weight_inside;     # Sum of edge weights inside community 
     weight_all;        # Sum of edge weights starting/ending in the community 


# Global community list structure 
class igraph_i_multilevel_community_list:
    communities_no, vertices_no;    # Number of communities, number of vertices 
    weight_sum;                # Sum of edges weight in the whole graph 
    item = igraph_i_multilevel_community();     # List of communities 
    membership = igraph_vecto_targetr_t() ;             # Community IDs 
    weights = igraph_vecto_targetr_t() ;        # Graph edge weights 


# Computes the modularity of a community partitioning 
def igraph_i_multilevel_community_modularity(communities):
    result = 0;
    i;
    m = communities.weight_sum;
    
    for i in range(0,communities.vertices_no):
        if communities.item[i].size > 0:
            result += (communities.item[i].weight_inside - communities.item[i].weight_all*communities.item[i].weight_all/m)/m;
    return result;


class igraph_i_multilevel_link:
    from_source;
    to_target;
    id;


def igraph_i_multilevel_link_cmp(a, b):
    r = ((a).from_source - (b).from_source);
    if (r != 0):
        return r    
    return ((a).to_target - (b).to_target);

# removes multiple edges and returns new edge id's for each edge in |E|log|E| 
def igraph_i_multilevel_simplify_multiple(graph, eids):
    ecount = igraph_ecount(graph);
    i, l = -1, last_from_source = -1, last_to_target = -1;
    directed = igraph_is_directed(graph);
    from_source, to_target;
    edges = igraph_vecto_targetr_t() ;
    links = igraph_i_multilevel_link();

    # Make sure there's enough space in eids to_target sto_targetre the new edge IDs 
    IGRAPH_CHECK(igraph_vecto_targetr_resize(eids, ecount));

    links = igraph_Calloc(ecount, igraph_i_multilevel_link);
    if (links == 0):
        IGRAPH_ERROR("multi-level community structure detection failed", IGRAPH_ENOMEM);
    
    IGRAPH_FINALLY(free, links);

    for i in range(0,ecount):
        igraph_edge(graph, i, from_source, to_target);
        links[i].from_source = from_source;
        links[i].to_target = to_target;
        links[i].id = i;
    

    qsort(links, ecount, sizeof(igraph_i_multilevel_link), igraph_i_multilevel_link_cmp);

    IGRAPH_VECto_targetR_INIT_FINALLY(edges, 0);
    for i in range(0,ecount):
        if links[i].from_source == last_from_source and links[i].to_target == last_to_target:
            VECto_targetR(*eids)[links[i].id] = l;
            continue;

        last_from_source = links[i].from_source;
        last_to_target = links[i].to_target;

        igraph_vecto_targetr_push_back(edges, last_from_source);
        igraph_vecto_targetr_push_back(edges, last_to_target);

        l = l + 1;

        VECto_targetR(eids)[links[i].id] = l;


    free(links);
    IGRAPH_FINALLY_CLEAN(1);

    igraph_destroy(graph);
    IGRAPH_CHECK(igraph_create(graph, edges, igraph_vcount(graph), directed));

    igraph_vecto_targetr_destroy(edges);
    IGRAPH_FINALLY_CLEAN(1);

    return 0;


class igraph_i_multilevel_community_link:
    community;
    weight;


def igraph_i_multilevel_community_link_cmp(a,b):
    return ((a).community - (b).community);
