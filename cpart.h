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
#endif
