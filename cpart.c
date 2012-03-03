#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpart.h"


float
dot_product(float v1[3], float v2[3])
{
	return (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]);
}

void
normalize(float v[3])
{
	float f = 1.0f / sqrt(dot_product(v, v));

	v[0] *= f;
	v[1] *= f;
	v[2] *= f;
}

void
cross_product(const float *v1, const float *v2, float *out)
{
	out[0] = v1[1] * v2[2] - v1[2] * v2[1];
	out[1] = v1[2] * v2[0] - v1[0] * v2[2];
	out[2] = v1[0] * v2[1] - v1[1] * v2[0];
}

void
multiply_vector_by_matrix(const float m[9], float v[3])
{
	float tmp[3];

	tmp[0] = v[0] * m[0] + v[1] * m[3] + v[2] * m[6];
	tmp[1] = v[0] * m[1] + v[1] * m[4] + v[2] * m[7];
	tmp[2] = v[0] * m[2] + v[1] * m[5] + v[2] * m[8];

	v[0] = tmp[0];
	v[1] = tmp[1];
	v[2] = tmp[2];
}
#define NUMDIM	3
#define RIGHT	0
#define LEFT	1
#define MIDDLE	2
char HitBoundingBox(minB,maxB, origin, dir,coord)
float minB[NUMDIM], maxB[NUMDIM];		/*box */
float origin[NUMDIM], dir[NUMDIM];		/*ray */
float coord[NUMDIM];				/* hit point */
{
	char inside = true;
	char quadrant[NUMDIM];
	register int i;
	int whichPlane;
	float maxT[NUMDIM];
	float candidatePlane[NUMDIM];

	/* Find candidate planes; this loop can be avoided if
   	rays cast all from the eye(assume perpsective view) */
	for (i=0; i<NUMDIM; i++)
		if(origin[i] < minB[i]) {
			quadrant[i] = LEFT;
			candidatePlane[i] = minB[i];
			inside = false;
		}else if (origin[i] > maxB[i]) {
			quadrant[i] = RIGHT;
			candidatePlane[i] = maxB[i];
			inside = false;
		}else	{
			quadrant[i] = MIDDLE;
		}

	/* Ray origin inside bounding box */
	if(inside)	{
		coord = origin;
		return (true);
	}


	/* Calculate T distances to candidate planes */
	for (i = 0; i < NUMDIM; i++)
		if (quadrant[i] != MIDDLE && dir[i] !=0.)
			maxT[i] = (candidatePlane[i]-origin[i]) / dir[i];
		else
			maxT[i] = -1.;

	/* Get largest of the maxT's for final choice of intersection */
	whichPlane = 0;
	for (i = 1; i < NUMDIM; i++)
		if (maxT[whichPlane] < maxT[i])
			whichPlane = i;

	/* Check final candidate actually inside box */
	if (maxT[whichPlane] < 0.) return (false);
	for (i = 0; i < NUMDIM; i++)
		if (whichPlane != i) {
			coord[i] = origin[i] + maxT[whichPlane] *dir[i];
			if (coord[i] < minB[i] || coord[i] > maxB[i])
				return (false);
		} else {
			coord[i] = candidatePlane[i];
		}
	return (true);				/* ray hits box */
}	

void tangent(Vector2 *out, Vector2 *a, Vector2 *b)
{
    out->x = (a->x-b->x)/2.0f;
    out->y = (a->y-b->y)/2.0f;
}
void CatmullRomSpline(Vector2 out[3], Vector2 *p0, Vector2 *p1, Vector2 *p2, Vector2 *p3) {
    Vector2 m0;
    //tangent(&m0, p1, p0);
    Vector2 m1;
    tangent(&m1, p2, p0);
    Vector2 m2;
    tangent(&m2, p3, p1);
    Vector2 m3;
    //tangent(&m3, p3, p2);
    float t = 0.0;
    //a = []
    //c = []
    for(int i=0; i<3;++i)
    {
        t = i*0.33333;
        float t_2 = t * t;
        float _1_t = 1 - t;
        float _2t = 2 * t;
        float h00 =  (1 + _2t) * (_1_t) * (_1_t);
        float h10 =  t  * (_1_t) * (_1_t);
        float h01 =  t_2 * (3 - _2t);
        float h11 =  t_2 * (t - 1);

        Vector2 result;
        //result.x = h00 * p0->x + h10 * m0.x + h01 * p1->x + h11 * m1.x;
        //result.y = h00 * p0->y + h10 * m0.y + h01 * p1->y + h11 * m1.y;
        //a.append(result)
        result.x = h00 * p1->x + h10 * m1.x + h01 * p2->x + h11 * m2.x;
        result.y = h00 * p1->y + h10 * m1.y + h01 * p2->y + h11 * m2.y;
        out[i] = result;
        //result = Vector2(0.0,0.0)
        //result.x = h00 * p2.x + h10 * m2.x + h01 * p3.x + h11 * m3.x;
        //result.y = h00 * p2.y + h10 * m2.y + h01 * p3.y + h11 * m3.y;
        //c.append(result)
    }
}


int ReadInt(char *str)
{
    int a;
    char littleEndian[4];
    for(int i=0;i<4;++i)
    {
        littleEndian[i] = str[3-i];
    }

    memcpy(&a, str, 4*sizeof(char));
    return a;
}
// 타일구조의 맵을 만들고 렌더링시에만 CatmullRomSpline으로 가로로 한번, 세로로 한번 계산해서 현재 쿼드의 4개의 선을 결정한다.
// 그런데 어떻게 하나?
// 현재 타일은 점 1개로 이루어져 있는데, 가로할땐 x-1, x, x+1, x+2로 해서 x~x+1까지의 점 4개의 x값을 얻어낸다.(x포함, x+0.25,x+0.5, x+0.75)
// 여기서 x값이란 바로 점의 Y(height)값 즉 높이를 나타낸다.
// 그래서 타일 하나로 아....존나 어렵구나. 그냥 버리자. 걍 리니어 인터폴레이션을 한다. 
// 아 그게 아니라.... 그냥 간단하게 애초에 스무딩 툴로 애초부터 타일 1개보다 좀 더 자잘한 버텍스들을 써서 타일 1개에 16개의 쿼드가 들어가게 한다?
// 아 그게 아니라 그냥 아예 그 뭐냐 DIgDig랑 똑같이 하되 좀 다르다. 2D맵이랑 비슷하다.
// 타일이 높으면 높고 낮으면 낮고. 2층은 그냥 아이템쌓기나 레이어 올리기 등으로 최대 5층까지만 층쌓기가 가능하도록 간단하게 한다.
/*
 
 */
// 아이템쌓기는 최대 255개까지?
// 3D이지만 울온이랑 똑같이(비슷하게) 구현한다.
