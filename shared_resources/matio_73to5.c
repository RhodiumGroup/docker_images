#include <stdlib.h>
#include <stdio.h>
#include "matio.h"

int main(int argc, char **argv) {
    mat_t    *matfp_in;
    mat_t    *matfp_out;
    matvar_t *matvar;
    matfp_in = Mat_Open(argv[1], MAT_ACC_RDONLY);
    if ( NULL == matfp_in ) {
        fprintf(stderr, "Error opening MAT file \"%s\"!\n", argv[1]);
        return EXIT_FAILURE;
    }
    matfp_out = Mat_CreateVer(argv[2], NULL, MAT_FT_MAT5);

    while ( (matvar = Mat_VarReadNext(matfp_in)) != NULL ) {
        printf("Writing MAT variable: %s... ", matvar->name);
        if (0 != Mat_VarWrite(matfp_out, matvar, MAT_COMPRESSION_NONE)) {
            printf("failed.\n");
        } else {
            printf("succeeded.\n");
        }
        Mat_VarFree(matvar);
    }
    
    Mat_Close(matfp_out);
    fprintf(stderr, "Wrote MAT file: \"%s\"\n", argv[2]);
    
    Mat_Close(matfp_in);
    return EXIT_SUCCESS;
}
