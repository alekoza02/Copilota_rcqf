#include <stdio.h>
#include <math.h>

void main() {}

int bb_test(void *bb_ptr, void *pos_ptr, void *dir_ptr) {
    
    int i;
    
    for (i = 0; i < 1000000; i++) {

        float *pos = (float *)pos_ptr;
        float *dir = (float *)dir_ptr;
        float *bb = (float *)bb_ptr;

        float bb_min[3];
        float bb_max[3];

        for (i = 0; i < 6; i++) {
            if (i < 3) {
                bb_min[i] = bb[i];
            } else {
                bb_max[i - 3] = bb[i];
            }
        } 

        float t_min = 0.0;
        float t_max = 1e6;

        for (i = 0; i < 3; i++) {
            if (dir[i] != 0.0) {
                float inv_dir = 1. / dir[i];

                float t1 = (bb_min[i] - pos[i]) * inv_dir;
                float t2 = (bb_max[i] - pos[i]) * inv_dir;

                float t_min_i = fmin(t1, t2);
                float t_max_i = fmax(t1, t2);

                t_min = fmax(t_min, t_min_i);
                t_max = fmin(t_max, t_max_i);

                if (t_min > t_max) {
                    return 0;
                }
            } else {
                if (pos[i] < bb_min[i] | pos[i] > bb_max[i]) {
                    return 0;
                }
            }
        }

        return 1;
    }
}

void introduce(){
    printf("Buongiorno, librerie C compilate e caricate correttamente!\n");
}