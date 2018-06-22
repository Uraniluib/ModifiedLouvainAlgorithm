# -- coding: utf-8 --
"""
Created on Thu Jun 21 01:20:50 2018

@author: Jinglin
"""

import ClassFile.py
import Modification.py

"""
    Given a graph, a community structure and a vertex ID, this method
    calculates:
 
    - edges: the list of edge IDs that are incident on the vertex
    - weight_all: the total weight of these edges
    - weight_inside: the total weight of edges that stay within the same
        community where the given vertex is right now, excluding loop edges
    - weight_loop: the total weight of loop edges
    - links_community and links_weight: together these two vectors list the
        communities incident on this vertex and the total weight of edges
        pointing to_target these communities
 """
def igraph_i_multilevel_community_links(graph,communities,edges,
                            weight_all,weight_inside,
                            weight_loop,links_community,links_weight):
    i, n, last = -1, c = -1;
    weight = 1;
    to_target, to_community;
    community = VECTOR(communities.membership)[vertex];
    links;

    weight_all = weight_inside = weight_loop = 0;

    igraph_vector_clear(links_community);
    igraph_vector_clear(links_weight);

    """ Get the list of incident edges """
    igraph_incident(graph, edges, vertex, IGRAPH_ALL);

    n = igraph_vector_size(edges);
    links = igraph_Calloc(n, igraph_i_multilevel_community_link);
    if links == 0:
            IGRAPH_ERROR("multi-level community structure detection failed", IGRAPH_ENOMEM);
    IGRAPH_FINALLY(igraph_free, links);

    for i in range(0,n):
        eidx = VECTOR(edges)[i];
        weight = VECTOR(communities.weights)[eidx];

        to_target = IGRAPH_OTHER(graph, eidx, vertex);

        weight_all += weight;
        if to_target == vertex:
            weight_loop += weight;
            links[i].community = community;
            links[i].weight = 0;
            continue;

        to_community = VECTOR((communities.membership))[to_target];
        if (community == to_community):
            weight_inside += weight;

        """ debug("Link %ld (C: %ld) <. %ld (C: %ld)\n", vertex, community, to_target, to_community); """
        
        links[i].community = to_community;
        links[i].weight = weight;

    """ Sort links by community ID and merge the same """
    qsort(links, n, sizeof(igraph_i_multilevel_community_link),
            igraph_i_multilevel_community_link_cmp);
    for i in range(0,n):
        to_community = links[i].community;
        if (to_community != last):
            igraph_vector_push_back(links_community, to_community);
            igraph_vector_push_back(links_weight, links[i].weight);
            last = to_community;
            c = c + 1;
        else:        
            VECTOR(links_weight)[c] += links[i].weight;

    igraph_free(links);
    IGRAPH_FINALLY_CLEAN(1);

    return 0


def igraph_i_multilevel_community_modularity_gain(communities,community,vertex,weight_all,weight_inside):
    IGRAPH_UNUSED(vertex);
    return weight_inside - communities.item[community].weight_allweight_all/communities.weight_sum;

""" Shrinks communities into single vertices, keeping all the edges.
    This method is internal because it destroys the graph in-place and
    creates a new one -- this is fine for the multilevel community
    detection where a copy of the original graph is used anyway.
    The membership vector will also be rewritten by the underlying
    igraph_membership_reindex call """
def igraph_i_multilevel_shrink(graph, membership):
    edges;
    no_of_nodes = igraph_vcount(graph);
    no_of_edges = igraph_ecount(graph);
    directed = igraph_is_directed(graph);

    i;
    eit;

    if (no_of_nodes == 0):
        return 0;

    if (igraph_vector_size(membership) < no_of_nodes):
        IGRAPH_ERROR("cannot shrink graph, membership vector too short",IGRAPH_EINVAL);


    IGRAPH_VECTOR_INIT_FINALLY(edges, no_of_edges*2);

    IGRAPH_CHECK(igraph_reindex_membership(membership, 0));

    """ Create the new edgelist """
    igraph_eit_create(graph, igraph_ess_all(IGRAPH_EDGEORDER_ID), eit);
    IGRAPH_FINALLY(igraph_eit_destroy, eit);
    i = 0;
    while (not IGRAPH_EIT_END(eit)):
        i = i+1;
        from_source, to_target;
        IGRAPH_CHECK(igraph_edge(graph, IGRAPH_EIT_GET(eit), from_source, to_target));
        VECTOR(edges)[i] = VECTOR(membership)[from_source];
        VECTOR(edges)[i] = VECTOR(membership)[to_target];
        IGRAPH_EIT_NEXT(eit);
        
    igraph_eit_destroy(eit);
    IGRAPH_FINALLY_CLEAN(1);

    """ Create the new graph """
    igraph_destroy(graph);
    no_of_nodes =  igraph_vector_max(membership)+1;
    IGRAPH_CHECK(igraph_create(graph, edges, no_of_nodes,directed));

    igraph_vector_destroy(edges);
    IGRAPH_FINALLY_CLEAN(1);

    return 0;


"""
    \ingroup communities
    \function igraph_i_community_multilevel_step
    \brief Performs a single step of the multi-level modularity optimization method
 
    This function implements a single step of the multi-level modularity optimization
    algorithm for finding community structure, see VD Blondel, J-L Guillaume,
    R Lambiotte and E Lefebvre: Fast unfolding of community hierarchies in large
    networks, http://arxiv.org/abs/0803.0476 for the details.
 
    This function was contributed by Tom Gregorovic.
 
    \param graph     The input graph. It must be an undirected graph.
    \param weights Numeric vector containing edge weights. If \c NULL, every edge
            has equal weight. The weights are expected to_target be non-negative.
    \param membership The membership vector, the result is returned here.
            For each vertex it gives the ID of its community.
    \param modularity The modularity of the partition is returned here.
            \c NULL means that the modularity is not needed.
    \return Error code.
 
    Time complexity: in average near linear on sparse graphs.
 """
def igraph_i_community_multilevel_step(graph,weights,membership,modularity):
    
    i, j;
    vcount = igraph_vcount(graph);
    ecount = igraph_ecount(graph);
    ffrom_source, fto;
    q, pass_q;
    pass_t;
    changed = 0;
    links_community;
    links_weight;
    edges;
    temp_membership;
    communities;

    """ Initial sanity checks on the input parameters """
    if (igraph_is_directed(graph)):
        IGRAPH_ERROR("multi-level community detection works for undirected graphs only",IGRAPH_UNIMPLEMENTED);
    if (igraph_vector_size(weights) < igraph_ecount(graph)):
        IGRAPH_ERROR("multi-level community detection: weight vector too short", IGRAPH_EINVAL);
    if (igraph_vector_any_smaller(weights, 0)):
        IGRAPH_ERROR("weights must be positive", IGRAPH_EINVAL);

    """ Initialize data structures """
    IGRAPH_VECTOR_INIT_FINALLY(links_community, 0);
    IGRAPH_VECTOR_INIT_FINALLY(links_weight, 0);
    IGRAPH_VECTOR_INIT_FINALLY(edges, 0);
    IGRAPH_VECTOR_INIT_FINALLY(temp_membership, vcount);
    IGRAPH_CHECK(igraph_vector_resize(membership, vcount));
 
    """ Initialize list of communities from_source graph vertices """
    communities.vertices_no = vcount;
    communities.communities_no = vcount;
    communities.weights = weights;
    communities.weight_sum = 2*igraph_vector_sum(weights);
    communities.membership = membership;
    communities.item = igraph_Calloc(vcount, igraph_i_multilevel_community);
    if (communities.item == 0):
        IGRAPH_ERROR("multi-level community structure detection failed", IGRAPH_ENOMEM);
    IGRAPH_FINALLY(igraph_free, communities.item);

    """ Still initializing the communities data structure """
    for i in range(0,vcount):
        VECTOR(communities.membership)[i] = i;
        communities.item[i].size = 1;
        communities.item[i].weight_inside = 0;
        communities.item[i].weight_all = 0;

    """ Some more initialization :) """
    for i in range(0,ecount):
        weight = 1;
        igraph_edge(graph, i, ffrom_source, fto_target);

        weight = VECTOR(weights)[i];
        communities.item[ffrom_source].weight_all += weight;
        communities.item[fto_target].weight_all += weight;
        if (ffrom_source == fto_target):
            communities.item[ ffrom_source].weight_inside += 2*weight;

    q = igraph_i_multilevel_community_modularity(communities);
    pass_t = 1;

    while changed and (q > pass_q):
        """ Pass begin """
        temp_communities_no = communities.communities_no;

        pass_q = q;
        changed = 0;
        
        """ Save the current membership, it will be restored in case of worse result """
        IGRAPH_CHECK(igraph_vector_update(temp_membership, communities.membership));

        for i in range(0,vcount):
            """ Exclude vertex from_source its current community """
            weight_all = 0;
            weight_inside = 0;
            weight_loop = 0;
            max_q_gain = 0;
            max_weight;
            old_id, new_id, n;

            igraph_i_multilevel_community_links(graph, communities, i, edges,
                                                weight_all, weight_inside,
                                                weight_loop, links_community, links_weight);

            old_id = VECTOR((communities.membership))[i];
            new_id = old_id;

            """ Update old community """
            igraph_vector_set(communities.membership, i, -1);
            communities.item[old_id].size = communities.item[old_id].size - 1;
            if (communities.item[old_id].size == 0):
                communities.communities_no = communities.communities_no - 1;
            communities.item[old_id].weight_all -= weight_all;
            communities.item[old_id].weight_inside -= 2 * weight_inside + weight_loop;

            """ debug("Remove %ld all: %lf Inside: %lf\n", i, -weight_all, -2weight_inside + weight_loop); """

            """ Find new community to_target join with the best modification gain """
            max_q_gain = 0;
            max_weight = weight_inside;
            n = igraph_vector_size(links_community);

            for j in range(0,n):
                c =  VECTOR(links_community)[j];
                w = VECTOR(links_weight)[j];

                q_gain = igraph_i_multilevel_community_modularity_gain(communities, c, i, weight_all, w);
                """ debug("Link %ld . %ld weight: %lf gain: %lf\n", i, c, (double) w, (double) q_gain); """
                if (q_gain > max_q_gain):
                    new_id = c;
                    max_q_gain = q_gain;
                    max_weight = w;

            """ debug("Added vertex %ld to_target community %ld (gain %lf).\n", i, new_id, (double) max_q_gain); """

            """ Add vertex to_target "new" community and update it """
            igraph_vector_set(communities.membership, i, new_id);
            if (communities.item[new_id].size == 0):
                communities.communities_no = communities.communities_no + 1;
            communities.item[new_id].size = communities.item[new_id].size + 1;
            communities.item[new_id].weight_all += weight_all;
            communities.item[new_id].weight_inside += 2 * max_weight + weight_loop;

            if (new_id != old_id):
                changed = changed + 1;

        q = igraph_i_multilevel_community_modularity(communities);

        if (changed and (q > pass_q)):
            """ debug("Pass %d (changed: %d) Communities: %ld Modularity from_source %lf to_target %lf\n",
                pass_t, changed, communities.communities_no, (double) pass_q, (double) q); """
            pass_t = pass_t + 1;
        else:
            """ No changes or the modularity became worse, restore last membership """
            IGRAPH_CHECK(igraph_vector_update(communities.membership, temp_membership));
            communities.communities_no = temp_communities_no;
            break;

        IGRAPH_ALLOW_INTERRUPTION();
    """ Pass end """

    if (modularity):
        modularity = q;


    """ debug("Result Communities: %ld Modularity: %lf\n",
        communities.communities_no, (double) q); """

    IGRAPH_CHECK(igraph_reindex_membership(membership, 0));

    """ Shrink the nodes of the graph according to_target the present community structure
        and simplify the resulting graph """

    """ TODO: check if we really need to_target copy temp_membership """
    IGRAPH_CHECK(igraph_vector_update(temp_membership, membership));
    IGRAPH_CHECK(igraph_i_multilevel_shrink(graph, temp_membership));
    igraph_vector_destroy(temp_membership);
    IGRAPH_FINALLY_CLEAN(1);    
    
    """ Update edge weights after shrinking and simplification """
    """ Here we reuse the edges vector as we don't need the previous contents anymore """
    """ TODO: can we use igraph_simplify here? """
    IGRAPH_CHECK(igraph_i_multilevel_simplify_multiple(graph, edges));

    """ We reuse the links_weight vector to_target store the old edge weights """
    IGRAPH_CHECK(igraph_vector_update(links_weight, weights));
    igraph_vector_fill(weights, 0);
     
    for i in range(0,ecount):
        VECTOR(weights)[VECTOR(edges)[i]] += VECTOR(links_weight)[i];

    igraph_free(communities.item);
    igraph_vector_destroy(links_community);
    igraph_vector_destroy(links_weight);
    igraph_vector_destroy(edges);
    IGRAPH_FINALLY_CLEAN(4);
    
    return 0;

"""
    \ingroup communities
    \function igraph_community_multilevel
    \brief Finding community structure by multi-level optimization of modularity
    
    This function implements the multi-level modularity optimization
    algorithm for finding community structure, see 
    VD Blondel, J-L Guillaume, R Lambiotte and E Lefebvre: Fast unfolding of
    community hierarchies in large networks, J Stat Mech P10008 (2008)
    for the details (preprint: http://arxiv.org/abs/arXiv:0803.0476).
 
    It is based on the modularity measure and a hierarchical approach.
    Initially, each vertex is assigned to_target a community on its own. In every step,
    vertices are re-assigned to_target communities in a local, greedy way: each vertex
    is moved to_target the community with which it achieves the highest contribution to_target
    modularity. When no vertices can be reassigned, each community is considered
    a vertex on its own, and the process starts again with the merged communities.
    The process stops when there is only a single vertex left or when the modularity
    cannot be increased any more in a step.
 
    This function was contributed by Tom Gregorovic.
 
    \param graph The input graph. It must be an undirected graph.
    \param weights Numeric vector containing edge weights. If \c NULL, every edge
         has equal weight. The weights are expected to_target be non-negative.
    \param membership The membership vector, the result is returned here.
         For each vertex it gives the ID of its community. The vector
         must be initialized and it will be resized accordingly.
    \param memberships Numeric matrix that will contain the membership
            vector after each level, if not \c NULL. It must be initialized and
            it will be resized accordingly.
    \param modularity Numeric vector that will contain the modularity score
            after each level, if not \c NULL. It must be initialized and it
            will be resized accordingly.
    \return Error code.
 
    Time complexity: in average near linear on sparse graphs.
    
    \example examples/simple/igraph_community_multilevel.c
 """

def igraph_community_multilevel(graph, weights, membership, memberships, modularity):
 
    g;
    w, m, level_membership;
    prev_q = -1, q = -1;
    i, level = 1;
    vcount = igraph_vcount(graph);

    """ Make a copy of the original graph, we will do the merges on the copy """
    IGRAPH_CHECK(igraph_copy(g, graph));
    IGRAPH_FINALLY(igraph_destroy, g);

    if (weights):
        IGRAPH_CHECK(igraph_vector_copy(w, weights));     
        IGRAPH_FINALLY(igraph_vector_destroy, w);    
    else:
        IGRAPH_VECTOR_INIT_FINALLY(w, igraph_ecount(g));
        igraph_vector_fill(w, 1);

    IGRAPH_VECTOR_INIT_FINALLY(m, vcount);
    IGRAPH_VECTOR_INIT_FINALLY(level_membership, vcount);

    if (memberships or membership):
        """ Put each vertex in its own community """
        for i in range(0,vcount):
            VECTOR(level_membership)[i] = i;
    if (memberships):
        """ Resize the membership matrix to_target have vcount columns and no rows """
        IGRAPH_CHECK(igraph_matrix_resize(memberships, 0, vcount));
    if (modularity):
        """ Clear the modularity vector """
        igraph_vector_clear(modularity);
    
    while (1):
        """ Remember the previous modularity and vertex count, do a single step """
        step_vcount = igraph_vcount(g);

        prev_q = q;
        IGRAPH_CHECK(igraph_i_community_multilevel_step(g, w, m, q));

        """ Were there any merges? If not, we have to_target stop the process """
        if (igraph_vcount(g) == step_vcount or q < prev_q):
            break;

        if (memberships or membership):
            for i in range(0,vcount):
                """ Readjust the membership vector """
                VECTOR(level_membership)[i] = VECTOR(m)[ VECTOR(level_membership)[i]];

        if (modularity):
            """ If we have to_target return the modularity scores, add it to_target the modularity vector """
            IGRAPH_CHECK(igraph_vector_push_back(modularity, q));

        if (memberships):
            """ If we have to_target return the membership vectors at each level, store the new
                membership vector """
            IGRAPH_CHECK(igraph_matrix_add_rows(memberships, 1));
            IGRAPH_CHECK(igraph_matrix_set_row(memberships, level_membership, level - 1));

        """ debug("Level: %d Communities: %ld Modularity: %f\n", level,  igraph_vcount(&g),
            (double) q); """

        """ Increase the level counter """
        level = level + 1;

    """ It might happen that there are no merges, so every vertex is in its 
         own community. We still might want the modularity score for that. """
    if (modularity and igraph_vector_size(modularity) == 0):
        tmp;
        mod;
        i;
        IGRAPH_VECTOR_INIT_FINALLY(tmp, vcount);
        for i in range(0,vcount):
            VECTOR(tmp)[i]=i; 
        IGRAPH_CHECK(igraph_modularity(graph, tmp, mod, weights));
        igraph_vector_destroy(tmp);
        IGRAPH_FINALLY_CLEAN(1);
        IGRAPH_CHECK(igraph_vector_resize(modularity, 1));
        VECTOR(modularity)[0]=mod;

    """ If we need the final membership vector, copy it to_target the output """
    if (membership):
        IGRAPH_CHECK(igraph_vector_resize(membership, vcount));     
        for i in range(0,vcount):
            VECTOR(membership)[i] = VECTOR(level_membership)[i];

    """ Destroy the copy of the graph """
    igraph_destroy(g);

    """ Destroy the temporary vectors """
    igraph_vector_destroy(m);
    igraph_vector_destroy(w);
    igraph_vector_destroy(level_membership);
    IGRAPH_FINALLY_CLEAN(4);

    return 0;