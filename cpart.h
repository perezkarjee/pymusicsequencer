#ifndef __CPART_H__
#define __CPART_H__ 1

typedef struct tTile {
    float height;
    int tileData;
} Tile;
typedef struct tChunk {
    Tile *tiles;
    int x,y,z;
} Chunk;

typedef struct tVector2 {
    float x;
    float y;
} Vector2;
char HitBoundingBox(float minB[3],float maxB[3], float origin[3], float dir[3],float coord[3]);
int ReadInt(char *);
#endif
