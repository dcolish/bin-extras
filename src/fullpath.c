/* fullpath: resolve a fullpath to a file */
/* Why the hell doesn't this exist yet? */

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("%s\n", "No filename given");
        exit(1);
    }

    char name[PATH_MAX + 1];
    if (realpath(argv[1], name) != NULL) {
            printf("%s\n", name);
    }
    else {
        printf("%s\n", "Path resolution failed");
        exit(1);
    }
    
    return 0;
}
        
