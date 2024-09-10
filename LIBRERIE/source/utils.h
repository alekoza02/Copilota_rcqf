#ifndef UTILS_H
#define UTILS_H

// Structure declaration
typedef struct Vec{
    double valore[3];
    double modulo;
} Vec;

typedef struct Ray{
    Vec pos;
    Vec dir;
    Vec ups;
    Vec rig;
    Vec ao_dir;
} Ray;

typedef struct Materiale{
    Vec colore_diffusione;
    double forza_emissione;
    Vec colore_emissione;
    double roughness;
    double glossiness;
    int glass;
    double IOR;
} Materiale;

typedef struct Record{
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

typedef struct Sphere{
    Vec pos;
    Materiale mat;
    double radius;
    int index;
    Vec min_box;
    Vec max_box;
} Sphere;

typedef struct Triangle {
    Vec VertA;
    Vec VertB;
    Vec VertC;
    
    Vec edgeAB;
    Vec edgeAC;

    Vec mediana;

    Vec normal;
    
    Vec min_box;
    Vec max_box;

    int index;

} Triangle;


typedef struct BB {
    Vec min;
    Vec max;
    Vec center;
    Vec size;
} BB;


typedef struct Node{
    BB bounding_box;

    Triangle *triangoli_originali;
    int *indici_triangoli;
    int n_triangles;

    struct Node *childA;
    struct Node *childB;
    int depth;
} Node;


typedef struct BVH {
    Triangle *triangoli_originali;
    Node *root;
    Materiale mat;

    int stat1;
    int stat2;
    int stat3;

} BVH;


typedef struct Model {

    Triangle *triangoli;

    Materiale materiale;
    int index_model;

} Model;


typedef struct ThreadData {

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
    
    float *array;
    float *local_output;
    
    Sphere *scena_sfera;
    int size_scena_sfera;

    Model *scena_modello;
    int size_modelli;
    int size_triangoli;

    Ray *camera;
    double fov;
} ThreadData;


#endif