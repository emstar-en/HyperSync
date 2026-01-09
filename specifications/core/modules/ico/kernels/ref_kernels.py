# Minimal reference kernels for ICO E/S/H
import math

def dot(u,v):
    return sum(float(a)*float(b) for a,b in zip(u,v))

def norm(v):
    return math.sqrt(dot(v,v))

# Euclidean
class Euclid:
    @staticmethod
    def distance(x,y):
        return norm([xi-yi for xi,yi in zip(x,y)])
    @staticmethod
    def exp_map(x, v):
        return [xi+vi for xi,vi in zip(x,v)]
    @staticmethod
    def log_map(x, y):
        return [yi-xi for xi,yi in zip(x,y)]
    @staticmethod
    def parallel_transport(x,y,v):
        return v[:]  # flat

# Spherical unit S^n in R^{n+1}
class Sphere:
    @staticmethod
    def project(u):
        n = norm(u)
        if n == 0: raise ValueError('zero vector for sphere projection')
        return [ui/n for ui in u]
    @staticmethod
    def distance(x,y):
        # great-circle distance via arccos of dot
        c = max(-1.0, min(1.0, dot(x,y)))
        return math.acos(c)
    @staticmethod
    def exp_map(x, v):
        # v tangent at x (dot(x,v)=0). Move along geodesic
        theta = norm(v)
        if theta == 0: return x[:]
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        # tangential direction
        vt = [vi/theta for vi in v]
        y = [cos_t*xi + sin_t*vti for xi,vti in zip(x,vt)]
        return Sphere.project(y)
    @staticmethod
    def log_map(x, y):
        # project y on tangent at x
        c = max(-1.0, min(1.0, dot(x,y)))
        theta = math.acos(c)
        if theta == 0: return [0.0]*len(x)
        # tangent component
        # u = (y - cos(theta) x) / sin(theta)
        sin_t = math.sin(theta)
        if sin_t == 0:
            raise ValueError('log undefined at antipodal')
        u = [(yi - c*xi)/sin_t for xi,yi in zip(x,y)]
        return [theta*ui for ui in u]
    @staticmethod
    def parallel_transport(x,y,v):
        # transport v along geodesic x->y using Schild's ladder (one step approximation)
        # For Tier-1, approximate as projection onto tangent at y while preserving component orthogonal to y
        vy = dot(v,y)
        # remove normal component at y
        vt = [vi - vy*yi for vi,yi in zip(v,y)]
        return vt

# Hyperbolic Lorentz model H^n: minkowski metric diag(+,-,...)
class Hyperboloid:
    @staticmethod
    def minkowski_dot(x):
        return float(x[0])*float(x[0]) - sum(float(xi)*float(xi) for xi in x[1:])
    @staticmethod
    def project(x):
        # project to unit hyperboloid (t>0)
        s = sum(xi*xi for xi in x[1:])
        t = math.sqrt(1.0 + s)
        sign = 1.0
        return [sign*t] + [xi for xi in x[1:]]
    @staticmethod
    def distance(x,y):
        md = Hyperboloid.minkowski_dot(x), Hyperboloid.minkowski_dot(y)
        # assume both on manifold
        z = x[0]*y[0] - sum(xi*yi for xi,yi in zip(x[1:], y[1:]))
        z = max(1.0, z)
        return math.acosh(z)
    @staticmethod
    def log_map(x, y):
        # from Nickel & Kiela 2017 formulation
        md = x[0]*y[0] - sum(xi*yi for xi,yi in zip(x[1:], y[1:]))
        md = max(1.0, md)
        dist = math.acosh(md)
        if dist == 0:
            return [0.0]*len(x)
        # direction in ambient
        w0 = (y[0] - math.cosh(dist)*x[0])
        wi = [yi - math.cosh(dist)*xi for xi,yi in zip(x[1:], y[1:])]
        # normalize by sinh(dist)
        sh = math.sinh(dist)
        dir0 = w0/sh
        diri = [w/sh for w in wi]
        # tangent vector has 0 minkowski inner product with x; drop normal component numerically
        # return tangent part (ignore time component for tangent representation)
        return [dir0*dist] + [d*dist for d in diri]
    @staticmethod
    def exp_map(x, v):
        # v tangent at x. split time/spatial components
        # tangent Minkowski norm squared is negative: <v,v>_M = -||v_spatial||^2 + v0^2; for tangent at x, <x,v>_M=0
        # For practicality, use closed form: exp_x(v) = cosh(||v||) x + sinh(||v||) (v/||v||)
        # where ||v|| = sqrt( -<v,v>_M )
        v0 = v[0]
        vs = v[1:]
        mink_v = v0*v0 - sum(vi*vi for vi in vs)
        lam = math.sqrt(max(1e-18, -mink_v))
        if lam == 0:
            return x[:]
        c, s = math.cosh(lam), math.sinh(lam)
        # normalize tangent direction u
        u0 = v0/lam
        us = [vi/lam for vi in vs]
        y0 = c*x[0] + s*u0
        ys = [c*xi + s*ui for xi,ui in zip(x[1:], us)]
        # project numerically
        return Hyperboloid.project([y0]+ys)
    @staticmethod
    def parallel_transport(x,y,v):
        # Approximate: project v to tangent at y
        # Remove component along y under Minkowski metric
        # alpha = <v,y>_M / <y,y>_M = -<v,y>_M since <y,y>_M = -1
        vy = v[0]*y[0] - sum(vi*yi for vi,yi in zip(v[1:], y[1:]))
        alpha = -vy
        vt0 = v[0] + alpha*y[0]
        vts = [vi + alpha*yi for vi,yi in zip(v[1:], y[1:])]
        return [vt0] + vts
