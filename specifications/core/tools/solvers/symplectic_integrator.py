
import math

def step(q, p, H_func, dt, scheme='leapfrog'):
    """
    Perform a single step of symplectic integration.

    Args:
        q (list[float]): Generalized coordinates (position).
        p (list[float]): Generalized momenta.
        H_func (callable): Hamiltonian function H(q, p). 
                           Must return (dH/dq, dH/dp) tuple of vectors.
        dt (float): Time step.
        scheme (str): Integration scheme ('euler', 'leapfrog', 'yoshida4').

    Returns:
        tuple: (q_next, p_next)
    """

    if scheme == 'leapfrog':
        return _leapfrog_step(q, p, H_func, dt)
    elif scheme == 'euler':
        return _symplectic_euler_step(q, p, H_func, dt)
    elif scheme == 'yoshida4':
        return _yoshida4_step(q, p, H_func, dt)
    else:
        raise ValueError(f"Unknown scheme: {scheme}")

def _symplectic_euler_step(q, p, H_func, dt):
    """Symplectic Euler: 1st order."""
    dq_H, _ = H_func(q, p)
    p_next = [pi - dt * dqi for pi, dqi in zip(p, dq_H)]

    _, dp_H_next = H_func(q, p_next)
    q_next = [qi + dt * dpi for qi, dpi in zip(q, dp_H_next)]

    return q_next, p_next

def _leapfrog_step(q, p, H_func, dt):
    """Leapfrog (Verlet): 2nd order."""
    dq_H, _ = H_func(q, p)
    p_half = [pi - 0.5 * dt * dqi for pi, dqi in zip(p, dq_H)]

    _, dp_H_half = H_func(q, p_half)
    q_next = [qi + dt * dpi for qi, dpi in zip(q, dp_H_half)]

    dq_H_next, _ = H_func(q_next, p_half)
    p_next = [pi - 0.5 * dt * dqi for pi, dqi in zip(p_half, dq_H_next)]

    return q_next, p_next

def _yoshida4_step(q, p, H_func, dt):
    """
    Yoshida 4th Order Symplectic Integrator.
    Composition of 3 leapfrog steps with specific coefficients.
    """
    w0 = -1.7024143839193153
    w1 = 1.3512071919596578

    # Step 1
    q, p = _leapfrog_step(q, p, H_func, w1 * dt)
    # Step 2
    q, p = _leapfrog_step(q, p, H_func, w0 * dt)
    # Step 3
    q, p = _leapfrog_step(q, p, H_func, w1 * dt)

    return q, p
