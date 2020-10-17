import pygame
import neat
import os
import time
import random

pygame.font.init()

WIN_WIDTH = 550
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# STAT_FONT = pygame.font.SysFont("applecoloremojittc", 50)
# STAT_FONT = pygame.font.Font("/System/Library/Fonts/Supplemental/Comic Sans MS.ttf", 50)
STAT_FONT = pygame.font.Font("/System/Library/Fonts/Supplemental/Copperplate.ttc", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # after every jump we keep calling move() until another jump call is made.
    # Note inside the jump call we have saved the position from where it jumped
    # In move function inside the conditions for titling upwards or downwards
    # Consider the bird is moving upwards.
    # self.y is the current position of the moving bird (i.e the jump button is not pressed again yet)
    # self.height is the position of the bird from where last time the jump was called
    # if our bird is still above that position (i.e effectively it is still moving upwards and also ignoring the downward curve of the bird) then the equation self.y < self.height + 50
    # in self.height + 50 we actually are assuming the bird is above the point from where it jumped even if we have displaced the jump point 50 pixels in downward direction
    # in that situation we are not allowing the bird to have a crazy titling angle like 90 or 180 and so we set it to our max tilt angle i.e 25 degree

    def move(self):
        self.tick_count += 1
        # d is the distance in pixels moved
        # self.tick_count basically the count of time
        # d = ut + (1/2)at^2

        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # terminal velocity

        if displacement >= 16:
            displacement = 16

        # tuning the velocity if we are moving upwards
        if displacement < 0:
            displacement -= 2

        # adjusting the y co-ordinate of the bird according to the distance calculated

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            # we are checking this condition in every frame so if following one frame if the tilt angle exceeds 90 degrees we put it back to 90 degrees so that the doesnot undergo crazy amount of flipping

            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        # keep a track of how many times our image is shown or how many times it has passed through a while loop

        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:  # for less than 5 sec : flap up image
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:  # for 5 - 10 sec : flat flap image
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:  # for 10 - 15 sec : flap down image
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:  # for 15 - 20 sec : flap flat image
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:  # : flap up image and values are reseted
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:  # if the bird is tilting in the range of 80-90 degrees then the flapping of bird wont make sense
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2  # we satisfy the condition of flat flap so that when we start flying up again we dont miss a frame

        # Rotate the image about its center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # Draw the image of rotated bird
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        # self.gap = 10

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)

        # "top" is the top-left point from where we are drawing the image
        # now in order the figure out from where to draw the image i.e "top" we perform below expression
        # (random height - pipe image height)
        # print(PIPE_IMG.get_height()) i.e get_height is the height property of the image object
        # the expression will always evaluate negative value when we are considering the flip image of pipe i.e top pipe
        # The significance of this negative value is we start to draw the flip pipe outside of our window i.e it is not drawn and we get our required height

        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)  # None
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (0, 255, 0))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (0, 255, 0))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def pause(win):
    paused = True
    while paused:
        if paused:
            text = STAT_FONT.render("Paused", 1, (255, 0, 0))
            win.blit(text, (WIN_WIDTH / 2 - 60, WIN_HEIGHT / 2))
            pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

    pygame.time.Clock().tick(120)


def main(genomes, config):
    global GEN
    GEN += 1
    # bird = Bird(230, 350)
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)

        # provide the neural network to the nets list

        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    score = 0

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption('AI Flappy Bird')
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pause(win)


        # At a time there can be atmost 2 pipes in the screen.
        # to decide which from which pipe we need to calculate the distance we check the passing condition of the bird for first pipe

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        # we encourage the bird to move by increasing its fitness

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    # discourage the bird to hit the pipe

                    ge[x].fitness -= 1

                    # remove the bird from the network which collided

                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:  # bird and pipe
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:

            # every time the bird passes the pipe we encourage it more than just moving

            for g in ge:
                g.fitness += 5

            score += 1
            pipes.append(Pipe(700))

        for r in rem:
            pipes.remove(r)

        # When Bird hits the floor
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() > 730 or bird.y < 0:
                # we don't want to discourage the bird to move downwards so we don't decrease the fitness

                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    population = neat.Population(config)

    # StdOutReporter gives us the detailed information about our neural network

    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 100)  # no of generations
    pass


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
