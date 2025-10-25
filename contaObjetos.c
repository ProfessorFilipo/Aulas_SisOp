#include <stdio.h>

#define H 10
#define W 10

void MostraMatriz(int Matriz[H][W])
{
  int L, C;
  for(L=0; L<H; L++)
  {
    for(C=0; C<W; C++)
    {
      printf(" %c ", (Matriz[L][C]==0?'.':'#'));
    }
    printf("\n");
  }
}


int main()
{
  static int Matriz[H][W] = {{0,0,0,0,0,0,0,0,0,0}, 
                             {0,0,0,1,0,0,0,0,0,0},
                             {0,0,1,0,1,0,0,0,1,0},
                             {0,0,1,0,1,0,0,1,1,0},
                             {0,0,0,1,0,0,1,0,1,0},
                             {0,0,0,0,0,1,1,1,1,0},
                             {0,0,0,0,0,0,0,0,0,0},
                             {0,1,0,1,1,1,1,1,0,0},
                             {0,1,0,0,0,0,0,0,0,0},
                             {0,1,1,1,1,1,0,0,0,0}
                            };  
  
    MostraMatriz(Matriz);
    
}
