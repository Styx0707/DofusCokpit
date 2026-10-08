on(construct){
   loop4:
   while(true)
   {
      while(true)
      {
         if(!(0x27F83753 & 0x27F83753))
         {
            if(!ord("\x05"))
            {
               §§goto(addr001b);
            }
         }
         else
         {
            §§push(164910691);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 & _temp_1))
         {
            break;
         }
         break loop4;
      }
      §§goto(addr19dce);
   }
   loop6:
   while(true)
   {
      if(!ord("\x03"))
      {
         set(§§pop(),new §\§\§pop()§());
         set(§§constant(6),§§constant(7));
         set(§§constant(8),0);
         set(§§constant(9),true);
         set(§§constant(10),false);
         set(§§constant(11),§§constant(12));
         §§push(§§constant(13));
         §§push(§§constant(14));
         if(getTimer() + 1)
         {
            loop3:
            while(true)
            {
               set(§§pop(),§§pop());
               set(§§constant(15),§§constant(16));
               set(§§constant(17),§§constant(14));
               set(§§constant(18),false);
               set(§§constant(19),§§constant(20));
               §§push(§§constant(21));
               §§push(§§constant(20));
               if(false)
               {
                  §§push(new §\§\§pop()§());
                  break loop6;
               }
               set(§§pop(),§§pop());
               set(§§constant(22),§§constant(23));
               set(§§constant(24),§§constant(14));
               set(§§constant(25),false);
               set(§§constant(26),false);
               set(§§constant(27),§§constant(28));
               §§push(§§constant(29));
               §§push(false);
               loop1:
               while(true)
               {
                  set(§§pop(),§§pop());
                  set(§§constant(30),20);
                  set(§§constant(31),false);
                  set(§§constant(32),false);
                  set(§§constant(33),false);
                  set(§§constant(34),false);
                  §§push(§§constant(35));
                  §§push(false);
                  if(false)
                  {
                     startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                     while(true)
                     {
                        set("Y\x1d",false);
                        set(§§constant(1),false);
                        set(§§constant(2),false);
                        set(§§constant(3),true);
                        set(§§constant(4),false);
                        §§push(§§constant(5));
                        §§push(-1);
                        if(false)
                        {
                           §§push(getProperty(§§pop(), _X));
                           continue loop3;
                        }
                        §§goto(addr1a060);
                        continue loop6;
                     }
                     addr001b:
                     break loop5;
                     addr19e47:
                  }
                  else
                  {
                     addr19dce:
                  }
                  while(true)
                  {
                     set(§§pop(),§§pop());
                     set(§§constant(36),false);
                     set(§§constant(37),false);
                     set(§§constant(38),316);
                     set(§§constant(39),false);
                     set(§§constant(40),false);
                     §§push(§§constant(41));
                     §§push(false);
                     if(getTimer() + 1)
                     {
                        break loop6;
                     }
                     §§push(getProperty(§§pop(), _X));
                     continue loop1;
                  }
                  return;
               }
               break loop5;
               §§push(getProperty(§§pop(), _X));
               continue loop6;
               addr1a060:
            }
            §§goto(addr1a09b);
         }
         addr1a09b:
         return;
         §§push(§§pop()(§§pop()));
      }
      §§goto(addr19e47);
   }
   set(§§pop(),§§pop());
   §§goto(addr1a09b);
}
