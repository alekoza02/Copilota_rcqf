#ifndef EXAMPLE_H
#define EXAMPLE_H

// Structure declaration
typedef struct{
    float valore[3];
    float modulo;
} Vec;

typedef struct{
    Vec pos;
    Vec dir;
    Vec ups;
    Vec rig;
    Vec ao_dir;
} Ray;

typedef struct{
    Vec colore_diffusione;
    float forza_emissione;
    Vec colore_emissione;
    float roughness;
    float glossiness;
    int glass;
    float IOR;
} Materiale;

typedef struct{
    int test_eseguito;
    int hit;
    int index_sphere;
    float t;
    int front_face;
    Vec normale;
    Vec normale_rifrazione;
    Vec hit_pos;
    Materiale materiale;
} Record;

typedef struct{
    Vec pos;
    Materiale mat;
    float radius;
    int index;
    Vec min_box;
    Vec max_box;
} Sphere;

typedef struct {

    float seed;

    int max_threads;
    int samples;
    int bounces;
    int index;
    
    int width;
    int height;
    
    int start_x;
    int end_x;
    int start_y;
    int end_y;
    
    float *array;
    float *local_output;
    
    Sphere *scena;
    int size_scena;

    Ray *camera;
    float fov;
} ThreadData;

#endif