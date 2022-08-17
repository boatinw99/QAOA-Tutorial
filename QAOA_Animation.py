from manim import *
from math import *
from numpy import *
# constant related to animation
FLOW_COLOR = YELLOW_C

# Problem instance
# n is the number of qubits
n = 4
# if you want to animate the operators with other values please change the following variables accordingly
# cost = [C(0), C(1), ..., C(2^n -1)]
# param = [beta_1, beta_2, ... , beta_p, gamma_1, ... , gamma_p]
cost = array([4, 0, 0, 0, 0, -4, 0, 0, 0, 0, -4, 0, 0, 0, 0, 4])
param = array([1.01165847, -0.43173094, -1.15543623,  0.56370591])


N = 2**n
p = len(param)//2
beta = param[:p]
gamma = param[p:]

# mark the best element
mn = min(cost)

# set up text in animation
state_col = ["0"]*N
for i in range(N):
    if cost[i] == mn:
        state_col[i] = RED
    else:
        state_col[i] = BLUE

col = list(state_col)

state_text = []
for x in range(0, N):
    s = ""
    for i in range(0, n):
        if (1 << i) & x == 0:
            s = "0" + s
        else:
            s = "1" + s
    state_text.append("|"+s+"\\rangle")


# Keep track of the amplitude and phase
states = VGroup()
for i in range(N):
    states += Arrow(start=ORIGIN, end=[1/4, 0, 0], color=state_col[i],
                    max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0)

phase_tracker = [ValueTracker(0) for i in range(N)]
prob_tracker = [ValueTracker(states[i].get_length()**2) for i in range(N)]

v = VGroup()

def getText(text):
    return Tex(text, font_size=24).move_to([0, 3, 0])


glob_description = getText("Quantum approximate optimization algorithm")

# non-animation operations

def get2DLine(start, end, c=WHITE, w=1):
        return Line(start=start, end=end, color=c, stroke_opacity = 1, stroke_width=4/w)

def vectorAddition(v1: Arrow, v2: Arrow, c: color = BLUE):
    v = Arrow(start=ORIGIN, end=v2.get_end(), color=c,
              max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0).shift(v1.get_vector())
    v_add = Arrow(start=ORIGIN, end=v.get_end(), color=c,
                  max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0)
    return v_add


def vectorSubtraction(v1: Arrow, v2: Arrow, c: color):

    v_tmp2 = Arrow(start=ORIGIN, end=-v2.get_end(), color=c,
                   max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0)
    return vectorAddition(v1, v_tmp2, c)


def performPartialMixer(depth, x, y):

    # return a pair of new Arrows of x,y when performing partial mixer 'depth'
    v_add = vectorAddition(states[x], states[y], YELLOW_E)
    v_sub = vectorSubtraction(states[x], states[y], GREEN_E)

    v1_add = Arrow(start=ORIGIN, end=v_add.get_end()/2, color=YELLOW_E,
                   max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0).rotate_about_origin(-beta[depth])

    v1_sub = Arrow(start=ORIGIN, end=v_sub.get_end()/2, color=GREEN_E,
                   max_stroke_width_to_length_ratio=3.0, max_tip_length_to_length_ratio=0.15, buff=0).rotate_about_origin(beta[depth])

    vx = vectorAddition(v1_add, v1_sub, states[x].get_color())
    vy = vectorSubtraction(v1_add, v1_sub, states[y].get_color())

    return vx, vy


class cube(Scene):

    def construct(self):

        self.add(glob_description)
    
        # prepare cube
        dir_1 = array([-0.05, 2.5,0])
        s_0 = Circle().set_opacity(0.1).scale(0.1).move_to([-1, 0,0])

        s_2 = s_0.copy().shift([2.3,1,0])

        s_4 = s_0.copy().shift([2.25,-0.25,0])

        s_8 = s_0.copy().shift(dir_1).shift([0,-0.05,0])

        s_12 = s_4.copy().shift(dir_1)
        
        s_6 = s_4.copy().shift([2.3,1,0])

        s_10 = s_2.copy().shift(dir_1)

        s_14 = s_6.copy().shift(dir_1)


        s_2.shift([-0.5,0,0])
        s_14.shift([-0.5,0,0])
        s_6.shift([-0.5,0,0])
        s_10.shift([-0.5,0,0])

        s_2.shift([0.025,0.05,0])


        sta = VGroup(s_0, s_2, s_4, s_6, s_8, s_10, s_12,
                     s_14).shift([-2.75,-0.5,0]).scale(0.75)
        stb = sta.copy().shift([4.25, -2, 0])

        # add vertices
        for i in range(8):
            v.add(sta[i])
            v.add(stb[i])

        v.shift([-0.25,-0.5,0])
       
        for i in range(N):
            v[i].set_color(state_col[i])
        self.add_foreground_mobject(v)

        # add edges
        edges = VGroup()
        for x in range(N):
            for i in range(n):
                bits = 1 << i
                y = x ^ bits
                if(y > x):
                    edges.add(self.get_line(v[x], v[y]))
        self.add(edges)

        # add |0000>, |0001>, ... , |1111>
        state_description = VGroup(*[
            MathTex(state_text[i], font_size=14, color=col[i]).move_to(
                v[i].get_center()).shift([0.2, -0.2, 0])
            for i in range(N)
        ])
        self.add_foreground_mobject(state_description)

        # add probability 
        def get_prob(i):
            def prob():
                return MathTex("{:.2f}".format(prob_tracker[i].get_value()), font_size=16, color=col[i]).move_to(
                    v[i].get_center()).shift([0, 0.25, 0])
            return always_redraw(prob)
        probs = VGroup(*[
            get_prob(i)
            for i in range(N)
        ])
        self.add_foreground_mobject(probs)

        # add phase circle
        def get_phase_circle(i):
            def phase_vector():
                c = self.create_phase_circle(i)
                c[1].rotate_about_origin(phase_tracker[i].get_value())
                return c.move_to(v[i].get_center()).shift([0.3, 0, 0])
            return always_redraw(phase_vector)

        phase_circles = VGroup(*[
            get_phase_circle(i)
            for i in range(N)
        ])
        self.add_foreground_mobject(phase_circles)

        # iterate through each layer
        for i in range(p):
            # phase layer
            self.phaseLayer(depth=i)

            # mixer layer
            self.mixerLayer(depth=i)
            pass

        self.wait(15)

    def phaseLayer(self, depth):

        s = "Apply a phase operator " + \
            "$e^{-i\\gamma_" + f"{depth+1}" + "H_P}$" + \
            ", $\\gamma_" + f"{depth+1} = {gamma[depth]}$" 
        self.writeGlobText(s)
        for i in range(N):
            states[i].rotate_about_origin(angle=-gamma[depth]*cost[i])

        self.wait(2)
        self.play(*[
            phase_tracker[i].animate.increment_value(-gamma[depth]*cost[i])
            for i in range(N)
        ], run_time=3)

        for i in range(N):
            phase_tracker[i].set_value(states[i].get_angle())

        self.wait(2)

    def partialMixer(self, pos, depth):
        s = "Apply a partial mixing operator " + \
            "$e^{-i\\beta_" + f"{depth+1}" + "X_" + f"{pos}" + "}$" + \
            ", $\\beta_" + f"{depth+1} = {beta[depth]}$" 
        self.writeGlobText(s)
        # highlight edge
        highlight_edges = VGroup()
        mask = 1 << (n-pos)

        # flow
        anim_1 = VGroup()
        anim_2 = VGroup()
        anim_3 = VGroup()
        old_states = states.copy()
        for x in range(N):
            y = x ^ mask
            if y > x:
                vx, vy = performPartialMixer(depth, x, y)
                states[x].become(vx)
                states[y].become(vy)
                if states[x].get_length() == old_states[x].get_length() and states[x].get_angle() == old_states[x].get_angle() and \
                        states[y].get_length() == old_states[y].get_length() and states[y].get_angle() == old_states[y].get_angle():
                    continue

                highlight_edges.add(
                    get2DLine(v[x].get_center(), end=v[y].get_center(), w=6)
                )
                # amplitude goes from x1 -> y1
                x1 = x
                y1 = y
                if(states[x].get_length() >= old_states[x].get_length()):
                    # y goes to x
                    x1 = y
                    y1 = x

                prob_ch = states[y1].get_length()**2 - old_states[y1].get_length()**2
                th = 1 
                if prob_ch <= 0.05: 
                    th = 8
                elif prob_ch <= 0.1 :
                    th = 4
                elif prob_ch <= 0.3 :
                    th = 2 
                else :
                    th = 1
                
                p_st = get2DLine(v[x1].get_center(), v[x1].get_center(), c = FLOW_COLOR, w=th)
                line = get2DLine(v[x1].get_center(), v[y1].get_center(), c= FLOW_COLOR, w=th)
                p_ed = get2DLine(v[y1].get_center(), v[y1].get_center(), c= FLOW_COLOR, w=th)

                anim_1.add(p_st)
                anim_2.add(line)
                anim_3.add(p_ed)

        self.play(Create(highlight_edges))
        opacities = self.get_vertices_opacity()
        self.play(Create(anim_1))
        self.wait(1.75)

        self.play(*[
            anim_1[i].animate.become(anim_2[i])
            for i in range(N//2)
        ], run_time=4)

        self.play(*[
            anim_1[i].animate.become(anim_3[i])
            for i in range(N//2)
        ], run_time=4
        )
        self.play(*[
            phase_tracker[i].animate.set_value(states[i].get_angle())
            for i in range(N)
        ], *[
            v[i].animate.set_opacity(opacities[i])
            for i in range(N)
        ], *[
            prob_tracker[i].animate.set_value(states[i].get_length()**2)
            for i in range(N)
        ], run_time=3)

        self.wait(1.5)

        # fade the highlight edge
        self.play(FadeOut(highlight_edges))
        self.wait(2)

    def mixerLayer(self, depth):
        s = "Apply a mixing operator " + \
            "$e^{-i\\beta_" + f"{depth+1}" + "H_M}$" + \
            ", $\\beta_" + f"{depth+1} = {beta[depth]}$" 
        self.writeGlobText(s)
        for pos in range(n):
            self.partialMixer(pos+1, depth)
            pass

    def create_phase_circle(self, i: int):
        p = VGroup()
        p.add(Circle(color=col[i], stroke_width=0.5))
        phase = Vector(direction=[1, 0, 0], color=col[i],
                       stroke_width=2.0)
        p.add(phase)
        return p.scale(0.12)

    def get_vertices_opacity(self):
        opacities = []
        for x in range(N):
            sz = states[x].get_length()
            val = 0
            if sz <= 0.25:
                val = 0.1
            elif sz <= 0.5:
                r = 0.5
                l = 0.25
                # 0.02 before
                fr = 0.3
                fl = 0.1
                val = fl+((fr-fl)*(sz-l)/(r-l))
            elif sz <= 1:
                r = 1
                l = 0.5
                # 0.05 before
                fr = 0.5
                fl = 0.3
                val = fl+((fr-fl)*(sz-l)/(r-l))
            elif sz <= 3:
                r = 3
                l = 1
                fr = 1
                fl = 0.5
                val = fl+((fr-fl)*(sz-l)/(r-l))
            else:
                val = 1
            opacities.append(val)
        return opacities

    def get_line(self, sl: Circle, sr: Circle):
        return Line(start=sl.get_center(), end=sr.get_center(), color=GREY, stroke_opacity = 0.2, stroke_width=1)

    def writeGlobText(self, text):
        self.play(glob_description.animate.become(getText(text)))
        self.wait(2.5)
        pass
