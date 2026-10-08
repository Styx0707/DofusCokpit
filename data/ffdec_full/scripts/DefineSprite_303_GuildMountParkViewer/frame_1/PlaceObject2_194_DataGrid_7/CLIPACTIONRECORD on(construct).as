on(construct){
   loop3:
   while(true)
   {
      loop4:
      while(true)
      {
         if(!ord("\x04"))
         {
            if(false)
            {
               while(true)
               {
                  eval("\x01")[1] = 50;
                  eval("\x01")[2] = 222;
                  §§push("\t\n");
                  §§push(false);
                  if(!getTimer())
                  {
                     break;
                  }
                  §§goto(addr1bd81);
                  break loop4;
               }
               §§goto(addr1bd38);
               addr1bd03:
            }
         }
         else
         {
            §§push("\t");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop3;
      }
      §§pop()[§§pop()] = §§pop();
      §§goto(addr1bd03);
   }
   addr1bdec:
   if(getTimer() + 1)
   {
      cellRenderer = "MountParksViewerItem";
      set("\x16\x1d\x1b",[]);
      eval("\x16\x1d\x1b")[0] = "sortArea";
      loop5:
      while(true)
      {
         loop6:
         while(true)
         {
            §§push(eval("\x16\x1d\x1b"));
            §§push(1);
            §§push("minMax");
            if(!ord("\b"))
            {
               §§push(new §\§\§pop()§());
               while(true)
               {
                  set(§§pop(),§§pop());
                  set(§§constant(8),false);
                  set(§§constant(9),40);
                  set(§§constant(10),§§constant(11));
                  §§push(§§constant(12));
                  §§push(20);
                  break loop5;
                  startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                  §§push(new §\§\§pop()§());
               }
               §§goto(addr1be83);
               addr1bd81:
            }
            while(true)
            {
               §§pop()[§§pop()] = §§pop();
               eval(§§constant(2))[2] = §§constant(5);
               set(§§constant(6),[]);
               §§push(eval(§§constant(6)));
               §§push(0);
               §§push(283);
               if(getTimer() + 1)
               {
                  break loop4;
               }
               §§goto(addr1bdec);
               §§push(getProperty(§§pop(), _X));
               continue loop6;
            }
            break loop4;
         }
         addr1bd38:
         §§push(§§pop()(§§pop()));
         break;
      }
      set(§§pop(),§§pop());
      §§goto(addr1be83);
   }
   addr1be83:
}
