#ifndef __CPART_H__
#define __CPART_H__ 1

typedef struct tTile {
    int tileData;
} Tile;
typedef struct tChunk {
    Tile *tiles;
    int x,y,z;
} Chunk;


#endif
