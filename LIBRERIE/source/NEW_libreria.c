#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include "utils.h"

#ifdef _WIN32 // Only use __declspec(dllexport) on Windows
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT 
#endif

// Global flag variable
int FLAG_exit = 0; // Initialize flag to 0

DLLEXPORT void exit_procedure(){
    FLAG_exit = 1;
}

DLLEXPORT void start_procedure(){
    FLAG_exit = 0;
}


DLLEXPORT void reset_canvas(float *array, int w, int h) {
    for (int i = 0; i < w; i++){
        for (int j = 0; j < h; j++){
            array[(i * w + j) * 5 + 0] = 0.;
            array[(i * w + j) * 5 + 1] = 0.;
            array[(i * w + j) * 5 + 2] = 0.;
            array[(i * w + j) * 5 + 3] = 0.;
            array[(i * w + j) * 5 + 4] = 0.;
        }
    }
}


DLLEXPORT float *create_array(int w, int h) {
    float *array = (float*)malloc(w * h * 5 * sizeof(float));
    return array;
}


DLLEXPORT void free_array(float *ptr) {
    free(ptr);
    ptr = NULL;
}


// DLLEXPORT void main_loop(float *output, int w, int h){
//     for (int y = 0; y < h; y++){
//         for (int x = 0; x < w; x++){
//             output[(x * w + y) * 5 + 0] = (float)y / (float)w;
//             output[(x * w + y) * 5 + 1] = (float)x / (float)h;
//             output[(x * w + y) * 5 + 2] = 1.;
//         }
//     }
// }



// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// VECTOR DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


static inline Vec init_vettore(double values[3]){
    
    Vec vettore;

    for (int i = 0; i < 3; i++){
        vettore.valore[i] = values[i];
    }

    return vettore;
};


static inline double randomale(){
    double ris = (double)rand() / (double)RAND_MAX;
    return ris;
};

static inline double randomale_neg(){
    return ((.5 - randomale()) * 2);
};

static inline void modulo_vettore(Vec *vettore){
    double modulo = 0.0;
    
    for (int i = 0; i < 3; i++){
        modulo += vettore->valore[i] * vettore->valore[i];
    }
    
    vettore->modulo = sqrt(modulo);
};

static inline double no_void_modulo_vettore(Vec *vettore){
    double modulo = 0.0;
    
    for (int i = 0; i < 3; i++){
        modulo += vettore->valore[i] * vettore->valore[i];
    }
    
    return sqrt(modulo);
};


static inline void versore_vettore(Vec *vettore){
    modulo_vettore(vettore);
    
    for (int i = 0; i < 3; i++){
        vettore->valore[i] = vettore->valore[i] / vettore->modulo;
    };

    vettore->modulo = 1.0;

};


static inline Vec no_void_versore_vettore(Vec *vettore){
    modulo_vettore(vettore);

    Vec ris;
    
    for (int i = 0; i < 3; i++){
        ris.valore[i] = vettore->valore[i] / vettore->modulo;
    };

    vettore->modulo = 1.0;

    return ris;
};


static inline void inverti_vettore(Vec *vettore){
    for (int i = 0; i < 3; i++){
        vettore->valore[i] = - vettore->valore[i];
    };
};


static inline Vec somma_vettori(Vec *vettore1, Vec *vettore2){
    double ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] + vettore2->valore[i];
    }
    return init_vettore(ris);
};


static inline Vec differenza_vettori(Vec *vettore1, Vec *vettore2){
    double ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] - vettore2->valore[i];
    }
    return init_vettore(ris);
};


static inline double prodotto_scalare(Vec *vettore1, Vec *vettore2){

    double ris = 0.;
    for (int i = 0; i < 3; i++){
        ris += vettore1->valore[i] * vettore2->valore[i];
    }

    return ris;
};


static inline Vec scala_vettore(Vec *vettore1, double t){
    double ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] * t;
    }
    return init_vettore(ris);
};


static inline Vec prodotto_vettoriale(Vec *vettore1, Vec *vettore2){
    double ris[3] = {0., 0., 0.};
    ris[0] = vettore1->valore[1] * vettore2->valore[2] - vettore1->valore[2] * vettore2->valore[1];
    ris[1] = vettore1->valore[2] * vettore2->valore[0] - vettore1->valore[0] * vettore2->valore[2];
    ris[2] = vettore1->valore[0] * vettore2->valore[1] - vettore1->valore[1] * vettore2->valore[0];
    return init_vettore(ris);
};


static inline Vec prodotto_element_wise(Vec *vettore1, Vec *vettore2){
    double ris[3] = {0., 0., 0.};
    ris[0] = vettore1->valore[0] * vettore2->valore[0];
    ris[1] = vettore1->valore[1] * vettore2->valore[1];
    ris[2] = vettore1->valore[2] * vettore2->valore[2];
    return init_vettore(ris);
};


static inline Vec random_vector(){
    Vec ris;
    double arg[3];

    arg[0] = randomale_neg();
    arg[1] = randomale_neg();
    arg[2] = randomale_neg();

    ris = init_vettore(arg);

    versore_vettore(&ris);

    return ris;
}

static inline Vec rifletti(Vec *vettore1, Vec *normale){
    Vec ris;
    Vec tmp_v;

    double tmp_f = prodotto_scalare(vettore1, normale) * 2.0;
    tmp_v = scala_vettore(normale, tmp_f);
    ris = differenza_vettori(vettore1, &tmp_v);

    return ris;

}

static inline Vec lerp(Vec *vettore1, Vec *vettore2, double perc){
    Vec ris;

    ris.valore[0] = (1.0 - perc) * vettore1->valore[0] + perc * vettore2->valore[0];
    ris.valore[1] = (1.0 - perc) * vettore1->valore[1] + perc * vettore2->valore[1];
    ris.valore[2] = (1.0 - perc) * vettore1->valore[2] + perc * vettore2->valore[2];

    return ris;

}

static inline Vec minimo_vettore(Vec *vettore1, Vec *vettore2){
    Vec ris;

    for (int j = 0; j < 3; j++){
        ris.valore[j] = fmin(vettore1->valore[j], vettore2->valore[j]);
    }
    return ris;
}

static inline Vec massimo_vettore(Vec *vettore1, Vec *vettore2){
    Vec ris;
    for (int j = 0; j < 3; j++){
        ris.valore[j] = fmax(vettore1->valore[j], vettore2->valore[j]);
    }
    return ris;
}

static inline float indice_del_massimo_nel_vettore(Vec *vettore1){
    float controllo = vettore1->valore[0];
    int ris = 0;
    for (int i = 0; i < 3; i++){
        if (vettore1->valore[i] > controllo){
            controllo = vettore1->valore[i];
            ris = i;
        }
    }
    return ris;
}

static inline Vec BB_min_tri(Vec *vettore1, Vec *vettore2, Vec *vettore3){
    Vec ris;
    float tmp;

    for (int j = 0; j < 3; j++){
        tmp = fmin(vettore1->valore[j], vettore2->valore[j]);
        ris.valore[j] = fmin(tmp, vettore3->valore[j]);
    }
    return ris;
}

static inline Vec Mediana(Vec *vettore1, Vec *vettore2, Vec *vettore3){
    Vec ris;

    for (int j = 0; j < 3; j++){
        ris.valore[j] = (vettore1->valore[j] + vettore2->valore[j] + vettore3->valore[j]) / 3;
    }
    return ris;
}

static inline Vec BB_max_tri(Vec *vettore1, Vec *vettore2, Vec *vettore3){
    Vec ris;
    float tmp;

    for (int j = 0; j < 3; j++){
        tmp = fmax(vettore1->valore[j], vettore2->valore[j]);
        ris.valore[j] = fmax(tmp, vettore3->valore[j]);
    }
    return ris;
}

Vec ray_hit_where(Ray *raggio, double t){
    Vec risultato = scala_vettore(&raggio->dir, t);
    risultato = somma_vettori(&risultato, &raggio->pos);
    return risultato;
}


Vec ray_hit_how(Sphere *sfera, Record *record){
    Vec risultato = differenza_vettori(&record->hit_pos, &sfera->pos);
    versore_vettore(&risultato);
    return risultato;
}

void get_info_vettore(Vec *vettore){
    printf("Il valore del vettore e' : [");
    for (int i = 0; i < 3; i++){
        printf("%f, ", vettore->valore[i]);
    }
    printf("]\n");
};


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// HIT RECORD DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


void reset_record(Record *record){
    record->hit = 0;
    record->t = 1e6;
}

void check_front_face(Ray *raggio, Record *record){
    if (prodotto_scalare(&raggio->dir, &record->normale) > 0.0){
        record->front_face = 0;
        Vec tmp = record->normale;
        inverti_vettore(&tmp);
        record->normale_rifrazione = tmp;
    } else {
        record->front_face = 1;
        record->normale_rifrazione = record->normale;
    }
}


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// RAY DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


Ray init_raggio(double dir[3], double pos[3]){
    
    Ray raggio;

    raggio.pos = init_vettore(pos);
    raggio.dir = init_vettore(dir);

    return raggio;
};


Ray init_camera(double dir[3], double pos[3], double ups[3], double rig[3]){
    
    Ray raggio;

    raggio.pos = init_vettore(pos);
    raggio.dir = init_vettore(dir);
    raggio.ups = init_vettore(ups);
    raggio.rig = init_vettore(rig);

    return raggio;
};


void calc_bounce(Ray *raggio, Record *record){

    // DIFFUSE
    Vec ris_v = random_vector();

    if (prodotto_scalare(&record->normale, &ris_v) < 0){
        inverti_vettore(&ris_v);
    }

    raggio->ao_dir = ris_v;

    // BLOCCO MATERIALE DIFFUSE / SPECULAR / GLOSS
        
    if (record->materiale.glass == 0){

        // calcolo rimbalzo speculare
        Vec specular_ray = rifletti(&raggio->dir, &record->normale);

        // test specularità (1 True, 0 False)
        int is_specular = record->materiale.glossiness >= randomale();

        // combinazione roughness / metal / glossiness
        ris_v = lerp(&ris_v, &specular_ray, (1 - record->materiale.roughness) * is_specular);
        
    }

    // BLOCCO MATERIALE VETRO

    else if (record->materiale.glass == 1){
        
        // calcolo della direzione rifratta:
        // viene eseguito il check per raggio entrante ed uscente dall'oggetto. 
        // nel caso di raggio uscente viene testato inoltre l'angolo limite.
        // alla fine viene calcolata la probabilità di riflettanza dovuta alla legge di Brew.

        // controllo raggio entrante / uscente basato sulla faccia colpita (interna / esterna) 
        check_front_face(raggio, record);

        // calcolo del rapporto degli indici di rifrazione dei mezzi in base al raggio entrante / uscente (1.0 = aria)
        double ratio_rifrazione;
        if (record->front_face){
            ratio_rifrazione = 1 / record->materiale.IOR;
        } else {
            ratio_rifrazione = record->materiale.IOR;
        }

        // calcolo componenti trigonometriche
        double coseno = - prodotto_scalare(&raggio->dir, &record->normale_rifrazione);
        double seno = sqrt(1 - coseno * coseno);
        
        // calcolo probabilità di riflettanza di Brew usando approx. di Schlick
        double schlick_approx = (1 - record->materiale.IOR) / (1 + record->materiale.IOR);
        schlick_approx = schlick_approx * schlick_approx;
        
        // condizioni di rifrazione : 1 = riflettanza, 2 = angolo limite
        int cannot_refract1 = schlick_approx + (1 - schlick_approx) * (pow(1 - coseno, 5)) > randomale();
        int cannot_refract2 = ratio_rifrazione * seno > 1;

        Vec ris_g;

        if (cannot_refract1 | cannot_refract2){
            
            // non può rifrarre -> riflessione basata sulla normale interna
            ris_g = rifletti(&raggio->dir, &record->normale_rifrazione);
        
        } else {        
            
            // può rifrarre -> calcolo della nuova direzione con componente parallela e perpendicolare alla normale
            Vec tmp1 = scala_vettore(&record->normale_rifrazione, coseno);
            tmp1 = somma_vettori(&raggio->dir, &tmp1);
            Vec r_out_perp = scala_vettore(&tmp1, ratio_rifrazione);
            
            double sqrt_term = 1 - pow(no_void_modulo_vettore(&r_out_perp), 2);
            if (sqrt_term < 0){ 
                sqrt_term = - sqrt_term;
            }

            Vec r_out_para = scala_vettore(&record->normale_rifrazione, sqrt(sqrt_term));
            inverti_vettore(&r_out_para);


            ris_g = somma_vettori(&r_out_para, &r_out_perp);
        
        }

        // combinazione diffusa / vetro
        ris_v = lerp(&ris_g, &ris_v, record->materiale.roughness);
    }

    raggio->dir = ris_v;
    raggio->pos = record->hit_pos;

};


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// MATERIAL DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


Materiale init_materiale(double data[11]){
    Materiale mats;

    double arg[3];

    for (int i = 0; i < 3; i++){
        arg[i] = data[i];
    }

    Vec colore_diffusione = init_vettore(arg);

    for (int i = 4; i < 7; i++){
        arg[i - 4] = data[i];
    }

    Vec colore_emissione = init_vettore(arg);

    mats.colore_diffusione = colore_diffusione;
    mats.forza_emissione = data[3];
    mats.colore_emissione = colore_emissione;
    mats.roughness = data[7];
    mats.glossiness = data[8];
    mats.glass = (int)data[9];
    mats.IOR = data[10];

    return mats;

}


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// BVH DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


void GrowToInclude_tri(BB *bb, Triangle *triangle){
    
    bb->min = minimo_vettore(&bb->min, &triangle->min_box);
    bb->max = massimo_vettore(&bb->max, &triangle->max_box);
}


BB init_BB(Triangle *tris, int tri_size){

    BB ris;

    double arg1[3] = {1e12, 1e12, 1e12};
    double arg2[3] = {-1e12, -1e12, -1e12};
    
    ris.min = init_vettore(arg1);
    ris.max = init_vettore(arg2);

    for (int i = 0; i < tri_size; i++){
        GrowToInclude_tri(&ris, &tris[i]);
    }

    ris.center = somma_vettori(&ris.min, &ris.max);
    ris.center = scala_vettore(&ris.center, 0.5);
 
    ris.size = differenza_vettori(&ris.max, &ris.min);

    return ris;
}


void split(Node *parent, int depth, int *stat1, int *stat2, int *stat3) {
    
    parent->childA = NULL;
    parent->childB = NULL;

    // if (depth == 32) {
    //     (* stat1) += parent->n_triangles;
    //     (* stat2) += depth;
    //     (* stat3) += 1;
    //     return;
    // };
    
    int *Triangles_A = (int *)malloc(parent->n_triangles * sizeof(int));
    int *Triangles_B = (int *)malloc(parent->n_triangles * sizeof(int));

    if (Triangles_A == NULL || Triangles_B == NULL) {
        printf("Memory allocation failed\n");
        exit(1);
    }

    int indexA = 0;
    int indexB = 0;

    int inA = 0;

    int split_axis = indice_del_massimo_nel_vettore(&parent->bounding_box.size);
    
    for (int i = 0; i < parent->n_triangles; i++){
        
        inA = parent->bounding_box.center.valore[split_axis] > parent->triangoli_originali[parent->indici_triangoli[i]].mediana.valore[split_axis] ? 1 : 0;
        
        if (inA == 1){
            Triangles_A[indexA++] = parent->indici_triangoli[i];
        } else {
            Triangles_B[indexB++] = parent->indici_triangoli[i];
        }
    }
    
    Node *A = (Node *)malloc(sizeof(Node));

    parent->childA = A;

    A->triangoli_originali = parent->triangoli_originali;
    A->n_triangles = indexA;

    Triangles_A = (int *)realloc(Triangles_A, indexA * sizeof(int));
    A->indici_triangoli = Triangles_A;

    Triangle *Aarg = (Triangle *)malloc(indexA * sizeof(Triangle));

    for (int i = 0; i < indexA; i++){
        Aarg[i] = parent->triangoli_originali[A->indici_triangoli[i]];
    }

    A->bounding_box = init_BB(Aarg, indexA);
    A->depth = depth;

    free(Aarg);
    Aarg = NULL;

    if (indexA > 1 & A->n_triangles != parent->n_triangles){
        split(A, depth + 1, stat1, stat2, stat3);
    } else {
        (* stat1) += A->n_triangles;
        (* stat2) += depth;
        (* stat3) += 1;
        A->childA = NULL;
        A->childB = NULL;
    }

    // ---------------------------------------------------------

    Node *B = (Node *)malloc(sizeof(Node));
    
    parent->childB = B;

    B->triangoli_originali = parent->triangoli_originali;
    B->n_triangles = indexB;
    
    Triangles_B = (int *)realloc(Triangles_B, indexB * sizeof(int));
    B->indici_triangoli = Triangles_B;

    Triangle *Barg = (Triangle *)malloc(indexB * sizeof(Triangle));

    for (int i = 0; i < indexB; i++){
        Barg[i] = parent->triangoli_originali[B->indici_triangoli[i]];
    }

    B->bounding_box = init_BB(Barg, indexB);
    B->depth = depth;

    free(Barg);
    Barg = NULL;

    if (indexB > 1 & B->n_triangles != parent->n_triangles){
        split(B, depth + 1, stat1, stat2, stat3);
    } else {
        (* stat1) += B->n_triangles;
        (* stat2) += depth;
        (* stat3) += 1;
        B->childA = NULL;
        B->childB = NULL;
    }

    free(parent->indici_triangoli);
}


BVH build_BVH(Triangle *tris, int tri_size, Materiale *mat){
    

    BVH bvh;

    int *indici = (int *)malloc(tri_size * sizeof(int));

    for (int i = 0; i < tri_size; i++){
        indici[i] = tris[i].index;
    }

    bvh.triangoli_originali = tris;
    bvh.mat = (* mat);
    
    Node *root_alloc = (Node *)malloc(sizeof(Node));
    
    bvh.root = root_alloc;
    
    bvh.root->bounding_box = init_BB(bvh.triangoli_originali, tri_size);
    
    bvh.root->triangoli_originali = bvh.triangoli_originali;
    bvh.root->indici_triangoli = indici;
    bvh.root->n_triangles = tri_size;
    
    bvh.root->depth = 0;

    bvh.stat1 = 0;
    bvh.stat2 = 0;
    bvh.stat3 = 0;

    split(bvh.root, 1, &bvh.stat1, &bvh.stat2, &bvh.stat3);

    return bvh;

}


void free_node(Node *node){
    
    if (node->childA != NULL){
        free_node(node->childA);
    } 
    if (node->childB != NULL){
        free_node(node->childB);
    }

    free(node);    
}


void free_BVH(BVH *bvh){
    free_node(bvh->root);
}


static inline int hit_BB(BB *bounding_box, Ray *raggio){
    // Extract the minimum and maximum corners of the bounding box
    
    double t_min = 0.0;
    double t_max = 1e6;

    double inv_dir;

    double t1, t2;
    
    for (int i = 0; i < 3; i++){
        
        inv_dir = 1 / raggio->dir.valore[i];
        t1 = (bounding_box->min.valore[i] - raggio->pos.valore[i]) * inv_dir; 
        t2 = (bounding_box->max.valore[i] - raggio->pos.valore[i]) * inv_dir; 

        if (inv_dir < 0.0) {
            double tmp = t1;
            t1 = t2;
            t2 = tmp;
        } 

        t_min = fmax(t_min, t1);
        t_max = fmin(t_max, t2);
    }  

    int did_hit = t_max >= t_min & t_max > 0;

    return did_hit ? t_min : 1e12;
}


static inline int hit_triangle(Triangle *triangolo, Ray *raggio, Record *record){
    
    int successfull = 0;

    float determinante = - prodotto_scalare(&raggio->dir, &triangolo->normal);


    Vec ao = differenza_vettori(&raggio->pos, &triangolo->VertA);
    Vec dao = prodotto_vettoriale(&ao, &raggio->dir);

    float invDet = 1 / determinante;

    
    float t = prodotto_scalare(&ao, &triangolo->normal) * invDet;
    float u = prodotto_scalare(&triangolo->edgeAC, &dao) * invDet;
    float v = - prodotto_scalare(&triangolo->edgeAB, &dao) * invDet;
    float w = 1. - u - v;

    if (determinante > 1e-6 & t >= 0 & u >= 0 & v >= 0 & w >= 0 & t < record->t){

        successfull = 1;

        record->hit = 1;
        record->t = t;

        record->normale = no_void_versore_vettore(&triangolo->normal);;            
        record->hit_pos = ray_hit_where(raggio, record->t);
    }

    return successfull;

}


void attraversa_nodi(Node *node, Ray *raggio, Record *record, Materiale *mat){

    if (node->childA == NULL & node->childB == NULL){

        record->test_eseguito += node->n_triangles;

        for (int k = 0; k < node->n_triangles; k++){
            int did_tho = hit_triangle(&node->triangoli_originali[node->indici_triangoli[k]], raggio, record);
            if (did_tho){
                record->materiale = (* mat);
            }
        }
    
    } else if (node->childA != NULL & node->childB != NULL){

        float dstA = hit_BB(&node->childA->bounding_box, raggio);
        float dstB = hit_BB(&node->childB->bounding_box, raggio);

        // record->test_eseguito += 2;

        if (dstA > dstB){
            if (dstB < record->t) attraversa_nodi(node->childB, raggio, record, mat);
            if (dstA < record->t) attraversa_nodi(node->childA, raggio, record, mat);
        } else {
            if (dstA < record->t) attraversa_nodi(node->childA, raggio, record, mat);
            if (dstB < record->t) attraversa_nodi(node->childB, raggio, record, mat);
        }
    }
}


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// MODEL DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------

static inline int hit_BB_triangle(Triangle *tri, Ray *raggio){
    // Extract the minimum and maximum corners of the bounding box
    
    double t_min = 0.0;
    double t_max = 1e6;

    double inv_dir;

    double t1, t2;
    
    for (int i = 0; i < 3; i++){

        inv_dir = 1 / raggio->dir.valore[i];
        t1 = (tri->min_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
        t2 = (tri->max_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
        
        if (inv_dir < 0.0) {
            double tmp = t1;
            t1 = t2;
            t2 = tmp;
        } 

        t_min = fmax(t_min, t1);
        t_max = fmin(t_max, t2);
    
        if (t_max < t_min){
            return 0;
        }

    }  

    return 1;
}


static inline int hit_model(Model *modello, int tri_array_size, Ray *raggio, Record *record){
    
    for (int tri = 0; tri < tri_array_size; tri++){
        
        if (hit_BB_triangle(&modello->triangoli[tri], raggio)) {

            float determinante = - prodotto_scalare(&raggio->dir, &modello->triangoli[tri].normal);

            Vec ao = differenza_vettori(&raggio->pos, &modello->triangoli[tri].VertA);
            Vec dao = prodotto_vettoriale(&ao, &raggio->dir);

            float invDet = 1 / determinante;

            float t = prodotto_scalare(&ao, &modello->triangoli[tri].normal) * invDet;
            float u = prodotto_scalare(&modello->triangoli[tri].edgeAC, &dao) * invDet;
            float v = - prodotto_scalare(&modello->triangoli[tri].edgeAB, &dao) * invDet;
            float w = 1. - u - v;

            if (determinante > 1e-6 & t >= 0 & u >= 0 & v >= 0 & w >= 0 & t < record->t){

                record->hit = 1;
                record->t = t;
                record->materiale = modello->materiale;

                record->normale = no_void_versore_vettore(&modello->triangoli[tri].normal);;            
                record->hit_pos = ray_hit_where(raggio, record->t);
            }
        }
    }
}


Model init_modello(double *vertici, int n_tri, Materiale materiale){

    Model ris;

    ris.triangoli = (Triangle*)malloc(n_tri * sizeof(Triangle));
    
    if (ris.triangoli == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        exit(EXIT_FAILURE);  // Terminate the program with a failure status
    }

    for (int i = 0; i < n_tri; i++){
        Triangle build_triangle;

        double arg1[3] = {vertici[i * 9 + 0], vertici[i * 9 + 1], vertici[i * 9 + 2]};                    
        double arg2[3] = {vertici[i * 9 + 3], vertici[i * 9 + 4], vertici[i * 9 + 5]};                    
        double arg3[3] = {vertici[i * 9 + 6], vertici[i * 9 + 7], vertici[i * 9 + 8]};                

        build_triangle.VertA = init_vettore(arg1);
        build_triangle.VertB = init_vettore(arg2);
        build_triangle.VertC = init_vettore(arg3);

        build_triangle.edgeAB = differenza_vettori(&build_triangle.VertB, &build_triangle.VertA);
        build_triangle.edgeAC = differenza_vettori(&build_triangle.VertC, &build_triangle.VertA);
        
        build_triangle.normal = prodotto_vettoriale(&build_triangle.edgeAB, &build_triangle.edgeAC);

        build_triangle.max_box = BB_max_tri(&build_triangle.VertA, &build_triangle.VertB, &build_triangle.VertC);
        build_triangle.min_box = BB_min_tri(&build_triangle.VertA, &build_triangle.VertB, &build_triangle.VertC);

        build_triangle.mediana = Mediana(&build_triangle.VertA, &build_triangle.VertB, &build_triangle.VertC);

        build_triangle.index = i;

        ris.triangoli[i] = build_triangle;

    }

    ris.index_model = 0;
    ris.materiale = materiale;

    return ris;

}

// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// SPHERE DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


// Sphere init_sphere(double pos[3], double color[3], double radius, int index){
Sphere init_sphere(double pos[3], double radius, int index, Materiale mat){

    Sphere sfera;

    sfera.index = index;
    sfera.radius = radius;
    sfera.mat = mat;
    sfera.pos = init_vettore(pos);

    double arg[3] = {radius, radius, radius};

    Vec vettore_offset = init_vettore(arg);

    sfera.max_box = somma_vettori(&sfera.pos, &vettore_offset);
    inverti_vettore(&vettore_offset);
    sfera.min_box = somma_vettori(&sfera.pos, &vettore_offset);

    return sfera;

}


static inline int hit_BB_sphere(Sphere *sfera, Ray *raggio){
    // Extract the minimum and maximum corners of the bounding box
    
    double t_min = 0.0;
    double t_max = 1e6;

    double inv_dir;

    double t1, t2;
    
    for (int i = 0; i < 3; i++){

        inv_dir = 1 / raggio->dir.valore[i];
        t1 = (sfera->min_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
        t2 = (sfera->max_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
        
        if (inv_dir < 0.0) {
            double tmp = t1;
            t1 = t2;
            t2 = tmp;
        } 

        t_min = fmax(t_min, t1);
        t_max = fmin(t_max, t2);
    
        if (t_max < t_min){
            return 0;
        }

    }  

    return 1;
}


static inline int hit_sphere(Sphere *sfera, Ray *raggio, Record *record){

    Vec oc = differenza_vettori(&sfera->pos, &raggio->pos);

    double a = prodotto_scalare(&raggio->dir, &raggio->dir);
    double b = -2.0 * prodotto_scalare(&raggio->dir, &oc);
    double c = prodotto_scalare(&oc, &oc) - sfera->radius * sfera->radius;

    double discriminante = b * b - 4 * a * c;

    if (discriminante >= 0) {

        double sqrt_discr = sqrt(discriminante);
                
        double delta_min = (- b - sqrt_discr) / 2.0;
        double delta_max = (- b + sqrt_discr) / 2.0;
                
        if (delta_max > 0.001){

            double local_t = delta_max;

            if (delta_min > 0.001 && delta_min < delta_max){
                local_t = delta_min;
            }
        

            if (local_t < record->t){
                record->hit = 1;
                record->index_sphere = sfera->index;
                record->t = local_t;
                record->hit_pos = ray_hit_where(raggio, record->t);
                record->normale = ray_hit_how(sfera, record);
                record->materiale = sfera->mat;
            }
        }
    };
}


// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// RENDER STRUCTURE DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------

void* render_thread(void* arg) {


    // preparazione scena_sfera e data
    ThreadData* data = (ThreadData*)arg;
    
    srand((int)(data->seed * 10000));
    
    int num_threads = data->max_threads;
    int rows = sqrt(num_threads);
    
    Record record;
    Record record_ao;

    Sphere *scena_sfera = data->scena_sfera;
    Model *scena_modello = data->scena_modello;
    Ray *camera = data->camera;
    double fov = data->fov;
    int x = data->width;
    int y = data->height;
    int chunck_w = data->end_x - data->start_x;
    int chunck_h = data->end_y - data->start_y;
    int size_sfera = data->size_scena_sfera;
    int size_modelli = data->size_modelli;
    int size_triangoli = data->size_triangoli;

    // inizializzazione variabili
    Vec termine1;
    Vec termine2;
    Vec termine3;
    Ray camera_ray;
    camera_ray = init_raggio(camera->dir.valore, camera->pos.valore);

    // creazione BHV
    // time_t start_bvh = clock();  // Start the clock

    BVH bvh = build_BVH(scena_modello->triangoli, size_triangoli, &scena_modello->materiale);
    
    // printf("Statistica: Triangoli medi = %f, Profondità media = %f\n", (float)(bvh.stat1) / (float)(bvh.stat3), (float)(bvh.stat2) / (float)(bvh.stat3));

    // time_t end_bvh = clock();  double cpu_time_used = ((double) (end_bvh - start_bvh)) / CLOCKS_PER_SEC; printf("BVH generato in: %fs\n", cpu_time_used);

    // renderizzazione
    for (int k = 0; k < data->samples; k++){
        for (int i = 0; i < chunck_h; i++) {
            for (int j = 0; j < chunck_w; j++) {

                if (FLAG_exit == 1){free_BVH(&bvh); pthread_exit(NULL);}
                
                time_t start = clock();  // Start the clock

                // come ottenere la direzione -> somma delle 3 righe
                termine1 = scala_vettore(&camera->dir, (1 / tan(fov / 2))); 
                termine2 = scala_vettore(&camera->rig, (2 * (((data->start_x + j) + randomale_neg()) / x) - 1)); 
                termine3 = scala_vettore(&camera->ups, (2 * (((data->start_y + i) + randomale_neg()) / y) - 1) / (x/y)); 

                termine1 = somma_vettori(&termine1, &termine2);
                termine1 = somma_vettori(&termine1, &termine3);

                versore_vettore(&termine1);

                for (int k = 0; k < 3; k++){
                    camera_ray.dir.valore[k] = termine1.valore[k];
                }

                camera_ray.pos = camera->pos;

                double arg1[3] = {0., 0., 0.};
                double arg2[3] = {1., 1., 1.};

                Vec ray_incoming_light = init_vettore(arg1);
                Vec ray_color = init_vettore(arg2);

                // inizio bounces
                double color[3] = {0., 0., 0.};
                double normal[3] = {0., 0., 0.};
                double index[3] = {0., 0., 0.};
                double ao = 0.;
                int test_count = 0;


                for (int l = 0; l < data->bounces; l++){

                    // reset record
                    reset_record(&record);

                    for (int k = 0; k < size_sfera; k++){

                        // record.test_eseguito = 0;
                        if (hit_BB_sphere(&scena_sfera[k], &camera_ray)){
                            // record.test_eseguito = 1;
                            hit_sphere(&scena_sfera[k], &camera_ray, &record);
                        };

                        // test_count += record.test_eseguito;
                    }

                    // for (int k = 0; k < size_modelli; k++){
                    //     hit_model(&scena_modello[k], size_triangoli, &camera_ray, &record);
                    // }

                    record.test_eseguito = 0;
                    attraversa_nodi(bvh.root, &camera_ray, &record, &bvh.mat);
                    test_count += record.test_eseguito;

                    // AO save
                    if (l == 1){

                        // temp switch
                        Vec temp_memo = camera_ray.dir;
                        reset_record(&record_ao);
                        camera_ray.dir = camera_ray.ao_dir;

                        ao = 0.;

                        for (int k_ao = 0; k_ao < size_sfera; k_ao++){

                            // record_ao.test_eseguito = 0;
                            if (hit_BB_sphere(&scena_sfera[k_ao], &camera_ray)){
                                // record_ao.test_eseguito = 1;
                                hit_sphere(&scena_sfera[k_ao], &camera_ray, &record_ao);
                            };

                            // test_count += record_ao.test_eseguito;
                        }
                    
                        record.test_eseguito = 0;
                        attraversa_nodi(bvh.root, &camera_ray, &record_ao, &bvh.mat);
                        test_count += record.test_eseguito;
                        // for (int k = 0; k < size_modelli; k++){
                        //     hit_model(&scena_modello[k], size_triangoli, &camera_ray, &record_ao);
                        // }

                        if (record_ao.hit) {
                            Vec sub = differenza_vettori(&record_ao.hit_pos, &camera_ray.pos); 
                            modulo_vettore(&sub);
                            ao = 1 / (sub.modulo + 1);
                        }

                        camera_ray.dir = temp_memo;

                    }


                    if (record.hit) {

                        if (l == 0) {
                            double dot = - prodotto_scalare(&record.normale, &camera_ray.dir);

                            for (int l = 0; l < 3; l++){
                                versore_vettore(&record.normale);
                                normal[l] = (1. + record.normale.valore[l]) / 2.;
                                index[l] = record.materiale.colore_diffusione.valore[l] * dot;
                            }
                        }

                        calc_bounce(&camera_ray, &record);

                        Vec luce_emessa = scala_vettore(&record.materiale.colore_emissione, record.materiale.forza_emissione);
                        Vec tmp = prodotto_element_wise(&luce_emessa, &ray_color);
                        
                        // DEVELOPEMENT
                        ray_incoming_light = somma_vettori(&ray_incoming_light, &tmp);
                        ray_color = prodotto_element_wise(&ray_color, &record.materiale.colore_diffusione);


                    } else { 
                        break;
                    }

                
                }

                data->array[((data->start_y + i) * data->width + (data->start_x + j)) * 5 + 0] += ray_incoming_light.valore[0];
                data->array[((data->start_y + i) * data->width + (data->start_x + j)) * 5 + 1] += ray_incoming_light.valore[1];
                data->array[((data->start_y + i) * data->width + (data->start_x + j)) * 5 + 2] += ray_incoming_light.valore[2];
                data->array[((data->start_y + i) * data->width + (data->start_x + j)) * 5 + 3] += ao; ao = 0.;
                data->array[((data->start_y + i) * data->width + (data->start_x + j)) * 5 + 4] += test_count;
            }
        }

    }
    
    free_BVH(&bvh);
    pthread_exit(NULL);
}


DLLEXPORT int main_loop(float *output, int x, int y, double *pos, int size_pos, double *radii, int size_radii, double fov, double *camera_pos, double *camera_axes, int cores, int samples, int bounces, double *materiali, double seed, double *vertici_modelli, double *materiali_modelli, int *indici_modelli, int n_modelli, int n_triangoli) {

    // impostazioni
    int NUM_THREADS = cores;
    int row = sqrt(NUM_THREADS);

    pthread_t threads[NUM_THREADS];
    ThreadData thread_data[NUM_THREADS];

    // scena_sfera
    Sphere *scene_sfere[NUM_THREADS];

    for (int k = 0; k < NUM_THREADS; k++){
        scene_sfere[k] = (Sphere*)malloc(size_radii * sizeof(Sphere));
        
        if (scene_sfere[k] == NULL) {
            fprintf(stderr, "Memory allocation failed!\n");
            exit(EXIT_FAILURE);  // Terminate the program with a failure status
        }
    
        for (int i = 0; i < size_radii; i++){
            double arg_pos[3];
            
            arg_pos[0] = pos[i * 3 + 0];
            arg_pos[1] = pos[i * 3 + 1];
            arg_pos[2] = pos[i * 3 + 2];

            double arg_mat[11];

            for (int j = 0; j < 11; j++){
                arg_mat[j] = materiali[i * 11 + j];
            }

            Materiale mat = init_materiale(arg_mat);

            scene_sfere[k][i] = init_sphere(arg_pos, radii[i], i, mat);
        }
    }
    
    
    // scena_modello
    Model *scene_modello[NUM_THREADS];

    for (int k = 0; k < NUM_THREADS; k++){
        scene_modello[k] = (Model*)malloc(n_modelli * sizeof(Model));
        
        if (scene_modello[k] == NULL) {
            fprintf(stderr, "Memory allocation failed!\n");
            exit(EXIT_FAILURE);  // Terminate the program with a failure status
        }
    
        for (int i = 0; i < n_modelli; i++){

            double arg_mat[11];

            for (int j = 0; j < 11; j++){
                arg_mat[j] = materiali_modelli[i * 11 + j];
            }

            Materiale mat = init_materiale(arg_mat);

            scene_modello[k][i] = init_modello(vertici_modelli, n_triangoli, mat);
        }
    }

    // camera con raggio lanciato sullo schermo    
    double cam_pos[3];
    double cam_dir[3];
    double cam_ups[3];
    double cam_rig[3];

    for (int i = 0; i < 3; i++){
        cam_pos[i] = camera_pos[i];
        cam_rig[i] = camera_axes[i];
        cam_ups[i] = camera_axes[3 + i];
        cam_dir[i] = camera_axes[6 + i];
    }

    Ray camera = init_camera(cam_dir, cam_pos, cam_ups, cam_rig);
    inverti_vettore(&camera.ups);
    

    // Creating threads
    int combined_index;
    for (int i = 0; i < row; i++) {
        for (int j = 0; j < row; j++) {

            combined_index = i * row + j;

            thread_data[combined_index].seed = seed;

            thread_data[combined_index].max_threads = NUM_THREADS;
            thread_data[combined_index].samples = samples;
            thread_data[combined_index].bounces = bounces;
            thread_data[combined_index].index = combined_index;

            thread_data[combined_index].array = output;
            
            thread_data[combined_index].scena_sfera = scene_sfere[combined_index];
            thread_data[combined_index].size_scena_sfera = size_radii;
            
            thread_data[combined_index].scena_modello = scene_modello[combined_index];
            thread_data[combined_index].size_modelli = n_modelli;
            thread_data[combined_index].size_triangoli = n_triangoli;
            
            thread_data[combined_index].camera = &camera;
            thread_data[combined_index].fov = fov;

            thread_data[combined_index].width = x;
            thread_data[combined_index].height = y;

            if (j == row - 1){
                thread_data[combined_index].start_x = x - (x % row) - (x / row);
                thread_data[combined_index].end_x = x;
            } else {
                thread_data[combined_index].start_x = j * (x / row);
                thread_data[combined_index].end_x = (j + 1) * (x / row);
            };

            if (i == row - 1){
                thread_data[combined_index].start_y = y - (y % row) - (y / row);
                thread_data[combined_index].end_y = y;
            } else {
                thread_data[combined_index].start_y = i * (x / row);
                thread_data[combined_index].end_y = (i + 1) * (x / row);
            };
        }
    }

    for (int i = 0; i < row; i++) {
        for (int j = 0; j < row; j++) {

            if (pthread_create(&threads[i * row + j], NULL, render_thread, &thread_data[i * row + j])) {
                fprintf(stderr, "Error creating thread\n");
            }
        }
    }

    // Joining threads and collecting results
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }


    for (int k = 0; k < NUM_THREADS; k++){
        free(scene_sfere[k]);
        free(scene_modello[k]->triangoli);
        free(scene_modello[k]);
    }

    return 1;
}
