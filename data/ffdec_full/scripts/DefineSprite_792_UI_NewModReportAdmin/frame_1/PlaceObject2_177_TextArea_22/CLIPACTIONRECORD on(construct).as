on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(0x25D732B2 | 0x25D732B2))
         {
            if(!ord("\x07"))
            {
               while(true)
               {
                  set("i{invalid_utf8=150}\x04","@");
                  set("\b","@");
                  §§push("\x05");
                  §§push(true);
                  if(false)
                  {
                     §§pop() extends §§pop();
                     §§goto(addrbdcf);
                  }
                  §§goto(addrbe0e);
                  break loop3;
               }
               §§goto(addrbe0d);
               addrbdad:
            }
         }
         else
         {
            §§push(508574523);
         }
         if(!(§§pop() - 1))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      set(§§constant(13),§§constant(14));
      §§goto(addrbdad);
   }
   if(getTimer() + 1)
   {
      do
      {
         set("{invalid_utf8=150}\x05",false);
         set("\x07;;P\x1eQ{invalid_utf8=157}\x02",true);
         set("{invalid_utf8=176}",false);
         set("{invalid_utf8=136}\n",true);
         set("\x03",true);
         §§push("c");
         §§push(-1);
         if(!ord("\x03"))
         {
            addrbe0d:
            §§pop()[§§pop()] = §§pop();
            addrbe0e:
            set(§§pop(),§§pop());
            §§goto(addrbed3);
         }
         set(§§pop(),§§pop());
         set(§§constant(6),§§constant(7));
         set(§§constant(8),0);
         set(§§constant(9),true);
         set(§§constant(10),true);
         §§push(§§constant(11));
         §§push(§§constant(12));
         break loop3;
         §§pop() extends §§pop();
      }
      while(getTimer() + 1);
      addrbdcf:
   }
   duplicateMovieClip(§§pop(),§§pop(),§§pop());
   addrbed3:
}
