on(construct){
   loop5:
   while(true)
   {
      loop6:
      while(true)
      {
         if(!(0x2F1F1613 & 0x2F1F1613))
         {
            if(!ord("\x04"))
            {
               loop0:
               while(true)
               {
                  §§pop()[5] = 25;
                  while(true)
                  {
                     while(true)
                     {
                        §§push(eval("\x07\x05"));
                        §§push(6);
                        §§push(26);
                        if(!ord("\n"))
                        {
                           §§goto(addre08a);
                           §§push(§§pop()());
                        }
                        else
                        {
                           §§pop()[§§pop()] = §§pop();
                           set(§§constant(11),true);
                           set(§§constant(12),false);
                           set(§§constant(13),40);
                           set(§§constant(14),§§constant(15));
                           §§push(§§constant(16));
                           §§push(20);
                           if(ord("\x05"))
                           {
                              break loop0;
                           }
                           §§pop()[§§pop()] = §§pop();
                        }
                        §§goto(addre18a);
                     }
                     §§goto(addre148);
                  }
                  break loop6;
               }
               §§goto(addre149);
            }
         }
         else
         {
            §§push("\b");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop5;
      }
      continue loop0;
   }
   if(!(getTimer() + 1))
   {
      §§push(getProperty(§§pop(), _X));
      loop4:
      while(true)
      {
         eval(§§pop())[1] = "searchName";
         eval("\x16\x1d\x1b")[2] = "level";
         §§push(eval("\x16\x1d\x1b"));
         §§push(3);
         §§push("categoryName");
         if(!ord("\x03"))
         {
            §§pop() extends §§pop();
            break;
         }
         §§pop()[§§pop()] = §§pop();
         eval(§§constant(2))[4] = §§constant(7);
         eval(§§constant(2))[5] = §§constant(8);
         §§push(§§constant(2));
         loop2:
         while(true)
         {
            eval(§§pop())[6] = "\b\n\x1c{invalid_utf8=150}\n";
            set("\x07\x05",[]);
            eval("\x07\x05")[0] = 40;
            §§push(eval("\x07\x05"));
            §§push(1);
            §§push(125);
            if(!getTimer())
            {
               §§push(new §\§\§pop()§());
               while(true)
               {
                  set("{invalid_utf8=150}\x03","");
                  set("\b",[]);
                  eval("\b")[0] = "2{invalid_utf8=157}\x02";
                  §§push("\b");
                  if(!(getTimer() + 1))
                  {
                     break;
                  }
                  continue loop4;
               }
               break;
               addre117:
            }
            else
            {
               addre08a:
            }
            while(true)
            {
               §§pop()[§§pop()] = §§pop();
               eval("\x07\x05")[2] = 40;
               eval("\x07\x05")[3] = 80;
               §§push(eval("\x07\x05"));
               §§push(4);
               §§push(40);
               break loop6;
               §§push(§§pop()());
               continue loop2;
            }
            break;
         }
         addre149:
         set(§§pop(),new §\§\§pop()§());
         addre148:
         break;
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         §§goto(addre1bd);
         §§push(getProperty(§§pop(), _X));
      }
      return;
   }
   §§goto(addre117);
}
