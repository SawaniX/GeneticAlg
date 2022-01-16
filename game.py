import random
import pygame
import genetic_algorithm as ga
import time

width, height = 1100, 800  # width and height of the app window
screen = pygame.display.set_mode((width, height))  # create screen of the app
pygame.display.set_caption(
    "Simulation of the enviornment")  # add title of the window

refreshing = 60  # screen refreshing time per second

scale = 2  # 2 pixels = 1 cm in real life

robot_width, robot_length = 16, 26  # real robot width in cm, real robot length in cm
img = pygame.image.load('rob.png')  # load robot image to project
img_best = pygame.image.load('rob_best.png')
robot_img = pygame.transform.scale(
    img, (robot_width * scale, robot_length * scale))  # rescale image
img_best = pygame.transform.scale(
    img_best, (robot_width * scale, robot_length * scale))  # rescale image
#img = pygame.transform.rotate(robot_img, 180)

pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('arial', 30)
pygame.time.set_timer(pygame.USEREVENT, 100)

move_distance = 15  # distance that robot moves in one move in cm

l_dist, t_dist = 200, 200  # odleglosc sciany pomieszczenia od lewej i gornej krawedzi okna [w rzeczywistej odleglosci cm]
room_width, room_height = 150, 150  # real room dimensions in cm
outside_wall_thick = 10  # thickness of the outside walls
exit_width = 30  # real width of the doors in cm
exit_wall_width = (room_width - exit_width) / 2

robot_start_positions = [
    [l_dist * scale + 19 * scale, t_dist * scale + 105 * scale],
    [l_dist * scale + 50 * scale, t_dist * scale + 80 * scale],
    [l_dist * scale + 100 * scale, t_dist * scale + 20 * scale],
    [l_dist * scale + 30 * scale, t_dist * scale + 120 * scale],
    [l_dist * scale + 110 * scale, t_dist * scale + 100 * scale],
    [l_dist * scale + 90 * scale, t_dist * scale + 10 * scale],
    [l_dist * scale + 50 * scale, t_dist * scale + 100 * scale],
    [l_dist * scale + 10 * scale, t_dist * scale + 30 * scale],
    [l_dist * scale + 100 * scale, t_dist * scale + 60 * scale],
    [l_dist * scale + 60 * scale, t_dist * scale + 80 * scale]
]  # position of the left upper corner of the robot, here 19cm from left wall

black, white, green = (0, 0, 0), (255, 255, 255), (0, 255, 0)

maps = [[(l_dist * scale, t_dist * scale + 150, 150, 30), (0, 0, 0, 0)],
        [(l_dist * scale + 60, t_dist * scale + 100, 30, 30),
         (l_dist * scale + 200, t_dist * scale + 150, 30, 50)],
        [(l_dist * scale + 80, t_dist * scale + 130, 60, 30),
         (l_dist * scale + 200, t_dist * scale + 200, 30, 50)],
        [(l_dist * scale + 40, t_dist * scale + 90, 100, 30),
         (l_dist * scale + 150, t_dist * scale + 220, 30, 50)],
        [(l_dist * scale + 100, t_dist * scale + 150, 30, 30),
         (l_dist * scale + 200, t_dist * scale + 50, 30, 50)],
        [(l_dist * scale + 140, t_dist * scale + 100, 160, 30), (0, 0, 0, 0)],
        [(l_dist * scale + 91, t_dist * scale, 30, 80),
         (l_dist * scale + 140, t_dist * scale + 150, 80, 50)],
        [(l_dist * scale + 91, t_dist * scale, 30, 80),
         (l_dist * scale + 180, t_dist * scale + 200, 20, 80)],
        [(0, 0, 0, 0), (0, 0, 0, 0)],
        [(l_dist * scale + 160, t_dist * scale + 160, 80, 30),
         (l_dist * scale + 100, t_dist * scale + 100, 30, 50)]]


def rotate_robot(robot, img):  # draw robot in right front direction
    if robot.robot_direction == 0:
        screen.blit(img, (robot.pos.x, robot.pos.y))
    elif robot.robot_direction == 1:
        screen.blit(pygame.transform.rotate(img, 180),
                    (robot.pos.x, robot.pos.y))
    elif robot.robot_direction == 2:
        screen.blit(pygame.transform.rotate(img, -90),
                    (robot.pos.x - 10, robot.pos.y + 10))
    elif robot.robot_direction == 3:
        screen.blit(pygame.transform.rotate(img, 90),
                    (robot.pos.x - 10, robot.pos.y + 10))


def env(population, map, images, epoch):
    screen.fill(black)  # refresh screen

    # exterior walls
    pygame.draw.rect(screen, white,
                     (0, 0, width, outside_wall_thick))  # outside_wall_top
    pygame.draw.rect(screen, white,
                     (0, height - outside_wall_thick, width,
                      outside_wall_thick))  # outside_wall_bottom
    pygame.draw.rect(screen, white,
                     (0, 0, outside_wall_thick, height))  # outside_wall_left
    pygame.draw.rect(screen, white,
                     (width - outside_wall_thick, 0, outside_wall_thick,
                      height))  # outside_wall_right

    # room walls
    w1 = pygame.draw.rect(
        screen, white,
        (l_dist * scale, t_dist * scale, 1, room_height * scale))
    w2 = pygame.draw.rect(screen, white,
                          (l_dist * scale, t_dist * scale +
                           room_height * scale, room_width * scale, 1))
    w3 = pygame.draw.rect(screen, white,
                          (l_dist * scale + room_width * scale, t_dist * scale,
                           1, room_height * scale))  # right wall
    w4 = pygame.draw.rect(
        screen, white,
        (l_dist * scale, t_dist * scale, int(exit_wall_width * scale), 1))
    w5 = pygame.draw.rect(
        screen, white,
        (int(l_dist * scale + room_width * scale - exit_wall_width * scale),
         t_dist * scale, int(
             exit_wall_width * scale), 1))  # top wall of the room

    # obstacles
    ob1 = pygame.draw.rect(screen, white, maps[map][0])
    ob2 = pygame.draw.rect(screen, white, maps[map][1])

    # epoch text
    epoch_text = "Epoch: " + str(epoch)
    text_surface = my_font.render(epoch_text, False, (255, 255, 255))
    screen.blit(text_surface, (40, 40))
    for i in range(len(population)):
        rotate_robot(
            population[i], images[i]
        )  # draw robot in right front direction depends on robot_direction var
        rotate_robot(population[0], img_best)
        collision = False
        finish = False

        if population[i].robot_direction < 2:
            rec = pygame.Rect(population[i].pos.x, population[i].pos.y,
                              robot_width * scale, robot_length * scale)
        else:
            rec = pygame.Rect(population[i].pos.x - 10,
                              population[i].pos.y + 10, robot_length * scale,
                              robot_width * scale)

        if ob1.colliderect(rec) or ob2.colliderect(rec) or w1.colliderect(
                rec) or w2.colliderect(rec) or w3.colliderect(
                    rec) or w4.colliderect(rec) or w5.colliderect(rec):
            collision = True

        corner1 = (rec.x, rec.y)
        corner2 = (rec.x + rec.w, rec.y)
        corner3 = (rec.x, rec.y + rec.h)
        corner4 = (rec.x + rec.w, rec.y + rec.h)

        room_y_min = t_dist * scale
        room_y_max = t_dist * scale + room_height * scale
        room_x_min = l_dist * scale
        room_x_max = l_dist * scale + room_width * scale
        if corner1[1] < room_y_min and corner2[1] < room_y_min and corner3[
                1] < room_y_min and corner4[1] < room_y_min:
            finish = True
        elif corner1[1] > room_y_max and corner2[1] > room_y_max and corner3[
                1] > room_y_max and corner4[1] > room_y_max:
            finish = True
        elif corner1[0] < room_x_min and corner2[0] < room_x_min and corner3[
                0] < room_x_min and corner4[0] < room_x_min:
            finish = True
        elif corner1[0] > room_x_max and corner2[0] > room_x_max and corner3[
                0] > room_x_max and corner4[0] > room_x_max:
            finish = True

        population[i].did_reach_target = finish
        population[i].did_hit_wall = collision
    pygame.display.update()  # update screen


def forward(pos, robot_direction):
    if robot_direction == 0:
        pos.y += move_distance * scale
    elif robot_direction == 1:
        pos.y -= move_distance * scale
    elif robot_direction == 2:
        pos.x -= move_distance * scale
    elif robot_direction == 3:
        pos.x += move_distance * scale
    return pos


def turn_back(robot_direction):
    if robot_direction == 0:
        robot_direction = 1
    elif robot_direction == 1:
        robot_direction = 0
    elif robot_direction == 2:
        robot_direction = 3
    elif robot_direction == 3:
        robot_direction = 2
    return robot_direction


def left(robot_direction):  # rotate left
    if robot_direction == 0:
        robot_direction = 3
    elif robot_direction == 1:
        robot_direction = 2
    elif robot_direction == 2:
        robot_direction = 0
    elif robot_direction == 3:
        robot_direction = 1
    return robot_direction


def right(robot_direction):  # rotate right
    if robot_direction == 0:
        robot_direction = 2
    elif robot_direction == 1:
        robot_direction = 3
    elif robot_direction == 2:
        robot_direction = 1
    elif robot_direction == 3:
        robot_direction = 0
    return robot_direction


def find_center(pos,
                robot_direction):  # finds center of every edge of the robot
    up_down_x, up_y, down_y, right_left_y, left_x, right_x = 0, 0, 0, 0, 0, 0
    if robot_direction == 0 or robot_direction == 1:  # find center of top, lower, right and left edge
        up_down_x = pos.x + (robot_width * scale) / 2
        up_y = pos.y
        down_y = pos.y + robot_length * scale
        right_left_y = pos.y + (robot_length * scale) / 2
        left_x = pos.x
        right_x = pos.x + robot_width * scale
    elif robot_direction == 2 or robot_direction == 3:
        up_down_x = pos.x - 10 + (robot_length * scale) / 2
        up_y = pos.y + 10
        down_y = pos.y + 10 + robot_width * scale
        right_left_y = pos.y + 10 + (robot_width * scale) / 2
        left_x = pos.x - 10
        right_x = pos.x - 10 + robot_length * scale

    up = [up_down_x, up_y]
    down = [up_down_x, down_y]
    left_edge = [left_x, right_left_y]
    right_edge = [right_x, right_left_y]
    return up, down, left_edge, right_edge


def main():
    map = 6
    target_pos = [550, 380]

    clock = pygame.time.Clock(
    )  # clock to refresh screen refreshing frames per second
    run = True  # if it is False then quit program
    fit_sum = 0
    population_size = 100
    genom_size = 32
    population = ga.create_population(population_size, 6, genom_size)
    epoch = 0
    images = []
    for i in range(population_size):
        images.append(robot_img)

    step = 0
    count = 0

    while run:
        clock.tick(refreshing)
        if count == 0:
            env(population, map, images, epoch)
            count += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.USEREVENT:
                for val, robot in enumerate(population):
                    if not robot.did_hit_wall and not robot.did_reach_target:
                        if robot.genom[step] == 0:  # go forward
                            robot.pos = forward(robot.pos,
                                                robot.robot_direction)
                            # print("Robot nr " + str(val) + " przod")
                        if robot.genom[step] == 2:  # turn left and go forward
                            robot.robot_direction = left(robot.robot_direction)
                            # print("Robot nr " + str(val) + " left")
                        if robot.genom[step] == 3:  # go backward
                            robot.robot_direction = turn_back(
                                robot.robot_direction)
                            # print("Robot nr " + str(val) + " obrot")
                        if robot.genom[step] == 1:  # turn right and go forward
                            robot.robot_direction = right(
                                robot.robot_direction)
                            # print("Robot nr " + str(val) + " right")
                env(population, map, images, epoch)
                #print(population[0].pos, population[0].robot_direction)
                #print(population[1].pos, population[1].robot_direction)
                step += 1
                if step % genom_size == 0 and step != 0:
                    # jeśli wszystkie ruchy zostały zaanimowane, nowa epoka
                    epoch += 1
                    step = 0
                    fit_sum = 0
                    print("fintess:")
                    for robot in population:
                        robot.calulate_fitness(target_pos)
                        fit_sum += robot.fitness

                    population = ga.create_next_generation(
                        population, fit_sum, map)
                    print("#############")
                    print("NEW GENERATION")
                    print("#############")

    pygame.quit()


if __name__ == "__main__":
    main()
