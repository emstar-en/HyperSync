
import math

def vector_add(v1, v2):
    return [x + y for x, y in zip(v1, v2)]

def vector_sub(v1, v2):
    return [x - y for x, y in zip(v1, v2)]

def vector_scalar_mul(v, s):
    return [x * s for x in v]

def compute_gradient(image, width, height):
    """
    Computes the gradient of a 2D image (flattened list).
    Returns a list of (dx, dy) tuples.
    """
    grad = [(0.0, 0.0)] * (width * height)
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            
            # Forward difference for x
            if x < width - 1:
                dx = image[idx + 1] - image[idx]
            else:
                dx = 0.0
                
            # Forward difference for y
            if y < height - 1:
                dy = image[idx + width] - image[idx]
            else:
                dy = 0.0
                
            grad[idx] = (dx, dy)
    return grad

def compute_divergence(field, width, height):
    """
    Computes the divergence of a vector field (list of (dx, dy) tuples).
    Returns a flattened list representing the divergence image.
    """
    div = [0.0] * (width * height)
    for y in range(height):
        for x in range(width):
            idx = y * width + x
            (p1_x, p1_y) = field[idx]
            
            # Backward difference for x
            if x > 0:
                (p0_x, _) = field[idx - 1]
                dx = p1_x - p0_x
            else:
                dx = p1_x
                
            # Backward difference for y
            if y > 0:
                (_, p0_y) = field[idx - width]
                dy = p1_y - p0_y
            else:
                dy = p1_y
                
            div[idx] = dx + dy
    return div

def prox_l2(u, f, tau):
    """
    Proximal operator for L2 data fidelity term: 0.5 * ||u - f||^2
    prox_tau(u) = (u + tau * f) / (1 + tau)
    """
    return [(u_i + tau * f_i) / (1.0 + tau) for u_i, f_i in zip(u, f)]

def prox_l1_dual(p, sigma):
    """
    Projection onto the L2 ball for the dual variable (TV regularization).
    p is a list of (dx, dy) tuples.
    p_i = p_i / max(1, |p_i|/lambda) -> effectively projection onto unit ball if lambda=1
    Here we implement projection onto convex set K where sigma is step size.
    Actually for TV, the dual projection is p_i / max(1, |p_i|)
    """
    new_p = []
    for (dx, dy) in p:
        norm = math.sqrt(dx*dx + dy*dy)
        scale = 1.0
        if norm > 1.0:
            scale = 1.0 / norm
        new_p.append((dx * scale, dy * scale))
    return new_p

def pdhg_tv_denoising(noisy_image, width, height, lambda_tv, max_iters=100):
    """
    Performs Total Variation Denoising using PDHG algorithm.
    
    Args:
        noisy_image: Flattened list of pixel values.
        width: Image width.
        height: Image height.
        lambda_tv: Regularization parameter.
        max_iters: Number of iterations.
        
    Returns:
        Denoised image as a flattened list.
    """
    n_pixels = width * height
    
    # Primal variable u, initialized to noisy image
    u = list(noisy_image)
    # Dual variable p (gradient field), initialized to 0
    p = [(0.0, 0.0)] * n_pixels
    # Bar u (extrapolated primal)
    u_bar = list(u)
    
    # Step sizes
    L = math.sqrt(8.0) # Operator norm for gradient
    tau = 1.0 / L
    sigma = 1.0 / L
    theta = 1.0
    
    for k in range(max_iters):
        # 1. Dual update: p = prox_sigma*(p + sigma * grad(u_bar))
        grad_u_bar = compute_gradient(u_bar, width, height)
        p_step = [(p[i][0] + sigma * grad_u_bar[i][0], p[i][1] + sigma * grad_u_bar[i][1]) for i in range(n_pixels)]
        
        # Projection (prox for dual of L1 norm is projection onto L-inf ball, 
        # but for isotropic TV it's projection onto L2 ball of radius lambda? 
        # Standard TV dual constraint is |p| <= lambda. 
        # Let's assume standard ROF model: min |Du| + lambda/2 |u-f|^2
        # Then dual is projection onto ball of radius 1 (if lambda is in primal step) or similar.
        # Let's stick to standard projection onto unit ball for p.
        p = prox_l1_dual(p_step, sigma)
        
        # 2. Primal update: u_new = prox_tau(u - tau * div*(p))
        # div* is negative divergence
        div_p = compute_divergence(p, width, height)
        # u - tau * (-div p) = u + tau * div p
        # But adjoint of grad is -div. So K* = -div.
        # primal step: u_new = prox_G(u - tau * K*p) = prox_G(u + tau * div p)
        
        u_prev = list(u)
        term = [u[i] + tau * div_p[i] for i in range(n_pixels)]
        
        # Prox for data fidelity (L2 distance to noisy_image)
        # G(u) = lambda/2 ||u - f||^2
        # prox_tauG(v) = (v + tau*lambda*f) / (1 + tau*lambda)
        # Let's use the simple form where lambda is absorbed or explicit.
        # If minimizing ||u-f||^2 + lambda*TV(u)
        # prox is (v + tau*f)/(1+tau) if lambda is handled in dual?
        # Let's use the explicit formula:
        # u = (term + tau * noisy_image) / (1.0 + tau) # For lambda=1
        # With lambda:
        # u = (term + tau * lambda_tv * noisy_image) / (1.0 + tau * lambda_tv)
        # Wait, usually lambda multiplies the regularization term.
        # min 1/2||u-f||^2 + lambda |Du|
        # Primal step is prox_F(u - tau K* p) where F = 1/2||.-f||^2
        # prox_tauF(x) = (x + tau*f)/(1+tau)
        # Dual step handles lambda. Projection onto ball of radius lambda.
        
        # Let's adjust dual projection to radius lambda_tv
        # Re-do dual projection locally here for correctness with lambda parameter
        p_new_step = []
        for (dx, dy) in p_step:
            norm = math.sqrt(dx*dx + dy*dy)
            scale = 1.0
            if norm > lambda_tv:
                scale = lambda_tv / norm
            p_new_step.append((dx * scale, dy * scale))
        p = p_new_step
        
        # Primal prox (F = 1/2||u-f||^2)
        u = [(term[i] + tau * noisy_image[i]) / (1.0 + tau) for i in range(n_pixels)]
        
        # 3. Extrapolation
        u_bar = [u[i] + theta * (u[i] - u_prev[i]) for i in range(n_pixels)]
        
    return u
