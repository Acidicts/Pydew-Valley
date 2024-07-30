import pygame
from os import walk


def import_folder(path):
    surf_list = []

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            img_surf = pygame.image.load(full_path).convert_alpha()
            surf_list.append(img_surf)

    return surf_list


def import_folder_dict(path):
    surface_dict = {}

    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            img_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = img_surf

    return surface_dict
