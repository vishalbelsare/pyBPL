from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import torch


def get_variables(S, R, eps):
    """
    Indicate variables for optimization (requires_grad_)

    Parameters
    ----------
    S : list of Stroke
        TODO
    R : list of Relation
        TODO
    eps : float
        TODO

    Returns
    -------
    parameters : list
        list of optimizable parameters
    lbs : list
        list of lower bounds (each elem. is a tensor same size as param;
        empty list indicates no lb)
    ubs : list
        list of upper bounds (each elem. is a tensor; empty list indicates
        no ub)
    """
    parameters = []
    lbs = []
    ubs = []
    for s, r in zip(S, R):
        # shape
        s.shapes_type.requires_grad_()
        parameters.append(s.shapes_type)
        lbs.append([])
        ubs.append([])

        # scale
        s.invscales_type.requires_grad_()
        parameters.append(s.invscales_type)
        lbs.append(torch.full(s.invscales_type.shape, eps))
        ubs.append([])

    return parameters, lbs, ubs


def obj_fun(S, R, ctd):
    """
    Evaluate the log-likelihood of a character type under the prior

    Parameters
    ----------
    S : list of Stroke
        TODO
    R : list of Relation
        TODO

    Returns
    -------
    ll : tensor
        Scalar; log-likelihood under the prior.
    """
    # start the accumulator
    ll = 0.

    # loop through the strokes
    for s, r in zip(S, R):
        # log-prob of the control points for each sub-stroke in this stroke
        ll_cpts = ctd.score_shapes_type(s.ids, s.shapes_type)
        # log-prob of the scales for each sub-stroke in this stroke
        ll_scales = ctd.score_invscales_type(s.ids, s.invscales_type)
        # sum over sub-strokes and add to accumulator
        ll = ll + torch.sum(ll_cpts) + torch.sum(ll_scales)

    return ll


def optimize_type(
        char, ctd, lr, nb_iter, eps, projected_grad_ascent, show_examples=True
):
    """
    Take a character type and optimize its parameters to maximize the
    likelihood under the prior, using gradient descent

    Parameters
    ----------
    char : Character
        TODO
    ctd : CharacterTypeDist
        TODO
    lr : float
        TODO
    nb_iter : int
        TODO
    eps : float
        TODO
    projected_grad_ascent : bool
        TODO
    show_examples : bool
        TODO

    Returns
    -------
    score_list : list of float
        TODO

    """
    if show_examples:
        plt.figure(figsize=(4, 15))
    # get optimizable variables & their bounds
    parameters, lbs, ubs = get_variables(char.P, char.R, eps)
    # optimize the character type
    score_list = []
    i = 0
    nb_i = int(np.floor(nb_iter / 100))
    for idx in range(nb_iter):
        if idx % 100 == 0 and show_examples:
            print('iteration #%i' % idx)
            _, ex1 = char.sample_token().numpy()
            _, ex2 = char.sample_token().numpy()
            plt.subplot(nb_i, 2, 2 * i + 1)
            plt.imshow(ex1, cmap='Greys', vmin=0, vmax=1)
            plt.title('ex1')
            plt.ylabel('iter #%i' % idx)
            plt.subplot(nb_i, 2, 2 * i + 2)
            plt.imshow(ex2, cmap='Greys', vmin=0, vmax=1)
            plt.title('ex2')
            i += 1
        score = obj_fun(char.P, char.R, ctd)
        score.backward(retain_graph=True)
        score_list.append(score)
        with torch.no_grad():
            for ip, param in enumerate(parameters):
                # manual grad. ascent
                param.add_(lr * param.grad)
                if projected_grad_ascent:
                    lb = lbs[ip]
                    ub = ubs[ip]
                    if len(lb) > 0:
                        torch.max(param, lb, out=param)
                    if len(ub) > 0:
                        torch.min(param, ub, out=param)

                param.grad.zero_()

    return score_list