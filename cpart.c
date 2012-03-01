#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpart.h"


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
    for(i=0; i<3;++i)
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
// 타일구조의 맵을 만들고 렌더링시에만 CatmullRomSpline으로 가로로 한번, 세로로 한번 계산해서 현재 쿼드의 4개의 선을 결정한다.
// 그런데 어떻게 하나?
// 현재 타일은 점 1개로 이루어져 있는데, 가로할땐 x-1, x, x+1, x+2로 해서 x~x+1까지의 점 4개의 x값을 얻어낸다.(x포함, x+0.25,x+0.5, x+0.75)
// 여기서 x값이란 바로 점의 Y(height)값 즉 높이를 나타낸다.
// 그래서 타일 하나로 아....존나 어렵구나. 그냥 버리자. 걍 리니어 인터폴레이션을 한다. 
// 아 그게 아니라.... 그냥 간단하게 애초에 스무딩 툴로 애초부터 타일 1개보다 좀 더 자잘한 버텍스들을 써서 타일 1개에 16개의 쿼드가 들어가게 한다?
// 아 그게 아니라 그냥 아예 그 뭐냐 DIgDig랑 똑같이 하되 좀 다르다. 2D맵이랑 비슷하다.
// 타일이 높으면 높고 낮으면 낮고. 2층은 그냥 아이템쌓기나 레이어 올리기 등으로 최대 5층까지만 층쌓기가 가능하도록 간단하게 한다.
// 아이템쌓기는 최대 255개까지?
// 3D이지만 울온이랑 똑같이(비슷하게) 구현한다.
