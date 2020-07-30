#ifndef UTILS_SYSTEM_UNIX_H
#define UTILS_SYSTEM_UNIX_H
#define _XOPEN_SOURCE 700
#define _GNU_SOURCE 1
#define TEMP_FAILRE_RETRY(retvar, expression) do { \
    retvar = (expression); \
} while (retvar == -1 && errno == EINTR);
#endif
