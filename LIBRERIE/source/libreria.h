#ifndef EXAMPLE_H
#define EXAMPLE_H

// Structure declaration
typedef struct{
    double valore[3];
    double modulo;
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
    double forza_emissione;
    Vec colore_emissione;
    double roughness;
    double glossiness;
    int glass;
    double IOR;
} Materiale;

typedef struct{
    int test_eseguito;
    int hit;
    int index_sphere;
    double t;
    int front_face;
    Vec normale;
    Vec normale_rifrazione;
    Vec hit_pos;
    Materiale materiale;
} Record;

typedef struct{
    Vec pos;
    Materiale mat;
    double radius;
    int index;
    Vec min_box;
    Vec max_box;
} Sphere;

typedef struct {
    Vec VertA;
    Vec VertB;
    Vec VertC;
    
    Vec edgeAB;
    Vec edgeAC;

    Vec normal;
    
    Vec min_box;
    Vec max_box;
} Triangle;

typedef struct {

} BVH_node;

typedef struct {

    Triangle *triangoli;

    Materiale materiale;
    int index_model;

} Model;

typedef struct {

    double seed;

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
    
    double *array;
    double *local_output;
    
    Sphere *scena_sfera;
    int size_scena_sfera;

    Model *scena_modello;
    int size_modelli;
    int size_triangoli;

    Ray *camera;
    double fov;
} ThreadData;


#endif