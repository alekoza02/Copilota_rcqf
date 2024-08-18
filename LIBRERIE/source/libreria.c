#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
#include "libreria.h"


int* tester(int x, int y, int z) {
    int *array = (int*)malloc(x * y * z * sizeof(int));
    
    for (int i = 0; i < x; i++){
        for (int j = 0; j < y; j++){
            array[(i * x + j) * 3 + 0] = (int)(255 * i / x);
            array[(i * x + j) * 3 + 1] = (int)(255 * j / y);
            array[(i * x + j) * 3 + 2] = 255;
        }
    }

    return array;
}


void introduce(){
    printf("Buongiorno, librerie C caricate correttamente!\n");
}

// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// FREE ARRAY ALLOCATED MEMORY 
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------

void free_array(float *array) {
    free(array);
}

// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------
// VECTOR DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


Vec init_vettore(float values[3]){
    
    Vec vettore;

    for (int i = 0; i < 3; i++){
        vettore.valore[i] = values[i];
    }

    return vettore;
};


float randomale(){
    return (float)(rand() % 1000) / 1000;
};

float randomale_neg(){
    return (1 - (float)(rand() % 1000) / 500);
};

void modulo_vettore(Vec *vettore){
    float modulo = 0.0;
    
    for (int i = 0; i < 3; i++){
        modulo += vettore->valore[i] * vettore->valore[i];
    }
    
    vettore->modulo = sqrt(modulo);
};

float no_void_modulo_vettore(Vec *vettore){
    float modulo = 0.0;
    
    for (int i = 0; i < 3; i++){
        modulo += vettore->valore[i] * vettore->valore[i];
    }
    
    return sqrt(modulo);
};


void versore_vettore(Vec *vettore){
    modulo_vettore(vettore);
    
    for (int i = 0; i < 3; i++){
        vettore->valore[i] = vettore->valore[i] / vettore->modulo;
    };

    vettore->modulo = 1.0;

};


void inverti_vettore(Vec *vettore){
    for (int i = 0; i < 3; i++){
        vettore->valore[i] = - vettore->valore[i];
    };
};


Vec somma_vettori(Vec *vettore1, Vec *vettore2){
    float ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] + vettore2->valore[i];
    }
    return init_vettore(ris);
};


Vec differenza_vettori(Vec *vettore1, Vec *vettore2){
    float ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] - vettore2->valore[i];
    }
    return init_vettore(ris);
};


float prodotto_scalare(Vec *vettore1, Vec *vettore2){

    float ris = 0.;
    for (int i = 0; i < 3; i++){
        ris += vettore1->valore[i] * vettore2->valore[i];
    }

    return ris;
};


Vec scala_vettore(Vec *vettore1, float t){
    float ris[3] = {0., 0., 0.};
    for (int i = 0; i < 3; i++){
        ris[i] = vettore1->valore[i] * t;
    }
    return init_vettore(ris);
};


Vec prodotto_vettoriale(Vec *vettore1, Vec *vettore2){
    float ris[3] = {0., 0., 0.};
    ris[0] = vettore1->valore[1] * vettore2->valore[2] - vettore1->valore[2] * vettore2->valore[1];
    ris[1] = vettore1->valore[2] * vettore2->valore[0] - vettore1->valore[0] * vettore2->valore[2];
    ris[2] = vettore1->valore[0] * vettore2->valore[1] - vettore1->valore[1] * vettore2->valore[0];
    return init_vettore(ris);
};


Vec prodotto_element_wise(Vec *vettore1, Vec *vettore2){
    float ris[3] = {0., 0., 0.};
    ris[0] = vettore1->valore[0] * vettore2->valore[0];
    ris[1] = vettore1->valore[1] * vettore2->valore[1];
    ris[2] = vettore1->valore[2] * vettore2->valore[2];
    return init_vettore(ris);
};


Vec random_vector(){
    Vec ris;
    float arg[3];

    arg[0] = randomale_neg();
    arg[1] = randomale_neg();
    arg[2] = randomale_neg();

    ris = init_vettore(arg);

    versore_vettore(&ris);

    return ris;
}

Vec rifletti(Vec *vettore1, Vec *normale){
    Vec ris;
    Vec tmp_v;

    float tmp_f = prodotto_scalare(vettore1, normale) * 2.0;
    tmp_v = scala_vettore(normale, tmp_f);
    ris = differenza_vettori(vettore1, &tmp_v);

    return ris;

}

Vec lerp(Vec *vettore1, Vec *vettore2, float perc){
    Vec ris;

    ris.valore[0] = (1.0 - perc) * vettore1->valore[0] + perc * vettore2->valore[0];
    ris.valore[1] = (1.0 - perc) * vettore1->valore[1] + perc * vettore2->valore[1];
    ris.valore[2] = (1.0 - perc) * vettore1->valore[2] + perc * vettore2->valore[2];

    return ris;

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


Ray init_raggio(float dir[3], float pos[3]){
    
    Ray raggio;

    raggio.pos = init_vettore(pos);
    raggio.dir = init_vettore(dir);

    return raggio;
};


Ray init_camera(float dir[3], float pos[3], float ups[3], float rig[3]){
    
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
        float ratio_rifrazione;
        if (record->front_face){
            ratio_rifrazione = 1 / record->materiale.IOR;
        } else {
            ratio_rifrazione = record->materiale.IOR;
        }

        // calcolo componenti trigonometriche
        float coseno = - prodotto_scalare(&raggio->dir, &record->normale_rifrazione);
        float seno = sqrt(1 - coseno * coseno);
        
        // calcolo probabilità di riflettanza di Brew usando approx. di Schlick
        float schlick_approx = (1 - record->materiale.IOR) / (1 + record->materiale.IOR);
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
            
            float sqrt_term = 1 - pow(no_void_modulo_vettore(&r_out_perp), 2);
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


Materiale init_materiale(float data[11]){
    Materiale mats;

    float arg[3];

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
// SPHERE DEFINITION
// --------------------------------------------------------------------------------------------
// --------------------------------------------------------------------------------------------


// Sphere init_sphere(float pos[3], float color[3], float radius, int index){
Sphere init_sphere(float pos[3], float radius, int index, Materiale mat){

    Sphere sfera;

    sfera.index = index;
    sfera.radius = radius;
    sfera.mat = mat;
    sfera.pos = init_vettore(pos);

    float arg[3] = {radius, radius, radius};

    Vec vettore_offset = init_vettore(arg);

    sfera.max_box = somma_vettori(&sfera.pos, &vettore_offset);
    inverti_vettore(&vettore_offset);
    sfera.min_box = somma_vettori(&sfera.pos, &vettore_offset);

    return sfera;

}


Vec ray_hit_where(Ray *raggio, float t){
    Vec risultato = scala_vettore(&raggio->dir, t);
    risultato = somma_vettori(&risultato, &raggio->pos);
    return risultato;
}


Vec ray_hit_how(Sphere *sfera, Record *record){
    Vec risultato = differenza_vettori(&record->hit_pos, &sfera->pos);
    versore_vettore(&risultato);
    return risultato;
}


int hit_BB_sphere(Sphere *sfera, Ray *raggio){
    // Extract the minimum and maximum corners of the bounding box
    
    float t_min = 0.0;
    float t_max = 1e6;

    float inv_dir;

    float t1, t2, t_min_i, t_max_i;
    
    for (int i = 0; i < 3; i++){

        if (raggio->dir.valore[i] != 0.0){

            inv_dir = 1 / raggio->dir.valore[i];
            t1 = (sfera->min_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
            t2 = (sfera->max_box.valore[i] - raggio->pos.valore[i]) * inv_dir; 
            
            t_min_i = (t1 < t2) ? t1 : t2;
            t_max_i = (t1 > t2) ? t1 : t2;
            
            t_min = (t_min > t_min_i) ? t_min : t_min_i;
            t_max = (t_max < t_max_i) ? t_max : t_max_i;
            
            if (t_min > t_max){
                return 0;
            }
        
        } else {

            if (raggio->pos.valore[i] < sfera->min_box.valore[i] | raggio->pos.valore[i] > sfera->max_box.valore[i]){
                return 0;
            }
        }
    }  

    return 1;
}


int hit_sphere(Sphere *sfera, Ray *raggio, Record *record){

    Vec oc = differenza_vettori(&sfera->pos, &raggio->pos);

    float a = prodotto_scalare(&raggio->dir, &raggio->dir);
    float b = -2.0 * prodotto_scalare(&raggio->dir, &oc);
    float c = prodotto_scalare(&oc, &oc) - sfera->radius * sfera->radius;

    float discriminante = b * b - 4 * a * c;

    if (discriminante >= 0) {

        float sqrt_discr = sqrt(discriminante);
                
        float delta_min = (- b - sqrt_discr) / 2.0;
        float delta_max = (- b + sqrt_discr) / 2.0;
                
        if (delta_max > 0.001){

            float local_t = delta_max;

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


    // preparazione scena e data
    ThreadData* data = (ThreadData*)arg;
    
    srand((int)(data->seed * 10000));
    
    int num_threads = data->max_threads;
    int rows = sqrt(num_threads);
    
    Record record;

    Sphere *scena = data->scena;
    Ray *camera = data->camera;
    float fov = data->fov;
    int x = data->width;
    int y = data->height;
    int chunck_w = data->end_x - data->start_x;
    int chunck_h = data->end_y - data->start_y;
    int size = data->size_scena;

    // inizializzazione variabili
    Vec termine1;
    Vec termine2;
    Vec termine3;
    Ray camera_ray;
    camera_ray = init_raggio(camera->dir.valore, camera->pos.valore);
    
    // colore
    float color[3] = {0., 0., 0.};


    // set zero the array
    for (int i = 0; i < (chunck_h * chunck_w * 3); i++){
        data->local_output[i] = 0;
    }

    // renderizzazione
    for (int k = 0; k < data->samples; k++){
        for (int j = 0; j < chunck_w; j++) {
            for (int i = 0; i < chunck_h; i++) {

                // come ottenere la direzione -> somma delle 3 righe
                termine1 = scala_vettore(&camera->dir, (1 / tan(fov / 2))); 
                termine2 = scala_vettore(&camera->rig, (2 * (((data->start_x + i) + randomale_neg()) / x) - 1)); 
                termine3 = scala_vettore(&camera->ups, (2 * (((data->start_y + j) + randomale_neg()) / y) - 1) / (x/y)); 

                termine1 = somma_vettori(&termine1, &termine2);
                termine1 = somma_vettori(&termine1, &termine3);

                versore_vettore(&termine1);

                for (int k = 0; k < 3; k++){
                    camera_ray.dir.valore[k] = termine1.valore[k];
                }

                camera_ray.pos = camera->pos;

                float arg1[3] = {0., 0., 0.};
                float arg2[3] = {1., 1., 1.};

                Vec ray_incoming_light = init_vettore(arg1);
                Vec ray_color = init_vettore(arg2);

                // inizio bounces

                for (int l = 0; l < data->bounces; l++){

                    // reset record
                    reset_record(&record);

                    for (int k = 0; k < size; k++){
                        if (hit_BB_sphere(&scena[k], &camera_ray)){
                            hit_sphere(&scena[k], &camera_ray, &record);
                        }
                    }


                    if (record.hit) {

                        calc_bounce(&camera_ray, &record);

                        Vec luce_emessa = scala_vettore(&record.materiale.colore_emissione, record.materiale.forza_emissione);
                        Vec tmp = prodotto_element_wise(&luce_emessa, &ray_color);
                        ray_incoming_light = somma_vettori(&ray_incoming_light, &tmp);
                        ray_color = prodotto_element_wise(&ray_color, &record.materiale.colore_diffusione);

                        // for (int l = 0; l < 3; l++){
                        //     color[l] = (scena[record.index_sphere]).mat.colore_diffusione.valore[l];    // albedo
                        //     // color[l] = (1. + record.normale.valore[l]) / 2.;         // normale
                        
                        // }

                    } else { 
                        break;
                        // ray_incoming_light.valore[0] = 30. / 255.; // 37 
                        // ray_incoming_light.valore[1] = 30. / 255.; // 39 
                        // ray_incoming_light.valore[2] = 30. / 255.; // 56 
                    }

                
                }

                // fprintf(file, "%d %d %d\n", color[0], color[1], color[2]);
                data->local_output[(i * chunck_w + j) * 3 + 0] += ray_incoming_light.valore[0];
                data->local_output[(i * chunck_w + j) * 3 + 1] += ray_incoming_light.valore[1];
                data->local_output[(i * chunck_w + j) * 3 + 2] += ray_incoming_light.valore[2];
            
            }
        }
    }

    int r, g, b;

    for (int j = 0; j < chunck_w; j++) {
        for (int i = 0; i < chunck_h; i++) {

            // r = (int)(sqrt(data->local_output[(i * chunck_w + j) * 3 + 0] / data->samples) * 255.999);
            // g = (int)(sqrt(data->local_output[(i * chunck_w + j) * 3 + 1] / data->samples) * 255.999);
            // b = (int)(sqrt(data->local_output[(i * chunck_w + j) * 3 + 2] / data->samples) * 255.999);
            
            // if (r > 255){
            //     r = 255;
            // }
            // if (b > 255){
            //     b = 255;
            // }
            // if (g > 255){
            //     g = 255;
            // }

            // data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 0] = r;
            // data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 1] = g;
            // data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 2] = b;
            data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 0] = data->local_output[(i * chunck_w + j) * 3 + 0];
            data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 1] = data->local_output[(i * chunck_w + j) * 3 + 1];
            data->array[((data->start_x + i) * data->width + (data->start_y + j)) * 3 + 2] = data->local_output[(i * chunck_w + j) * 3 + 2];
        }
    }

    pthread_exit(NULL);
}


float* renderer_dispatcher(int x, int y, float *pos, int size_pos, float *radii, int size_radii, float fov, float *camera_pos, float *camera_axes, int cores, int samples, int bounces, float *materiali, float seed) {

    clock_t start = clock();

    // impostazioni
    float *output = (float*)malloc(x * y * 3 * sizeof(float));

    if (output == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        exit(EXIT_FAILURE);  // Terminate the program with a failure status
    }

    int NUM_THREADS = cores;
    int row = sqrt(NUM_THREADS);

    pthread_t threads[NUM_THREADS];
    ThreadData thread_data[NUM_THREADS];

    // scena
    Sphere *scene[NUM_THREADS];

    for (int k = 0; k < NUM_THREADS; k++){
        scene[k] = (Sphere*)malloc(size_radii * sizeof(Sphere));
        
        if (scene[k] == NULL) {
            fprintf(stderr, "Memory allocation failed!\n");
            exit(EXIT_FAILURE);  // Terminate the program with a failure status
        }
    
        for (int i = 0; i < size_radii; i++){
            float arg_pos[3];
            
            arg_pos[0] = pos[i * 3 + 0];
            arg_pos[1] = pos[i * 3 + 1];
            arg_pos[2] = pos[i * 3 + 2];

            float arg_mat[11];

            for (int j = 0; j < 11; j++){
                arg_mat[j] = materiali[i * 11 + j];
            }

            Materiale mat = init_materiale(arg_mat);

            scene[k][i] = init_sphere(arg_pos, radii[i], i, mat);
        }
    }


    // camera con raggio lanciato sullo schermo    
    float cam_pos[3];
    float cam_dir[3];
    float cam_ups[3];
    float cam_rig[3];

    for (int i = 0; i < 3; i++){
        cam_pos[i] = camera_pos[i];
        cam_rig[i] = camera_axes[i];
        cam_ups[i] = camera_axes[3 + i];
        cam_dir[i] = camera_axes[6 + i];
    }

    Ray camera = init_camera(cam_dir, cam_pos, cam_ups, cam_rig);
    inverti_vettore(&camera.ups);
        
    float *outputs_local[NUM_THREADS];


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
            
            thread_data[combined_index].scena = scene[combined_index];
            thread_data[combined_index].size_scena = size_radii;

            thread_data[combined_index].camera = &camera;
            thread_data[combined_index].fov = fov;

            thread_data[combined_index].width = x;
            thread_data[combined_index].height = y;
            thread_data[combined_index].start_x = i * (x / row);
            thread_data[combined_index].end_x = (i + 1) * (x / row);
            thread_data[combined_index].start_y = j * (x / row);
            thread_data[combined_index].end_y = (j + 1) * (x / row);

            outputs_local[combined_index] = (float*)malloc(
                (thread_data[combined_index].end_x - thread_data[combined_index].start_x) * 
                (thread_data[combined_index].end_y - thread_data[combined_index].start_y) *
                3 *  
                sizeof(float)
            );

            if (outputs_local[combined_index] == NULL) {
                fprintf(stderr, "Memory allocation failed!\n");
                exit(EXIT_FAILURE);  // Terminate the program with a failure status
            }

            thread_data[combined_index].local_output = outputs_local[combined_index];
        
        }
    }

    for (int i = 0; i < row; i++) {
        for (int j = 0; j < row; j++) {

            if (pthread_create(&threads[i * row + j], NULL, render_thread, &thread_data[i * row + j])) {
                fprintf(stderr, "Error creating thread\n");
                return NULL;
            }
        }
    }

    time_t end = clock();  // Stop the clock

    // Calculate the elapsed time in seconds
    double cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;
    // printf("Time taken: %f seconds\n", cpu_time_used);


    // Joining threads and collecting results
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }


    for (int k = 0; k < NUM_THREADS; k++){
        free(scene[k]);
        free(outputs_local[k]);
    }

    return output;
}


void main() {}
