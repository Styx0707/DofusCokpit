on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(true or true))
         {
            if(false)
            {
               while(true)
               {
                  set("",0);
                  set("",4);
                  set("",0);
                  §§push("\x1d{invalid_utf8=150}\x07");
                  §§push(0);
                  if(false)
                  {
                     break;
                  }
                  set(§§pop(),§§pop());
                  set(§§constant(16),4);
                  set(§§constant(17),4);
                  set(§§constant(18),§§constant(19));
                  set(§§constant(20),10);
                  set(§§constant(21),20);
                  §§push(§§constant(22));
                  §§push(§§constant(23));
                  if(!ord("\b"))
                  {
                     duplicateMovieClip(§§pop(),§§pop(),§§pop());
                     §§goto(addr653fa);
                  }
                  else
                  {
                     addr653ab:
                     set(§§pop(),§§pop());
                  }
                  §§goto(addr65535);
                  break loop3;
               }
               §§goto(addr653ab);
               §§push(getProperty(§§pop(), _X));
               addr65375:
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
         break loop2;
      }
      set(§§pop(),§§pop());
      set(§§constant(11),false);
      §§goto(addr65375);
   }
   if(ord("\b"))
   {
      do
      {
         set("\x03",§§constant(1));
         set(§§constant(2),§§constant(3));
         set(§§constant(4),§§constant(3));
         set(§§constant(5),§§constant(6));
         set(§§constant(7),20);
         set(§§constant(8),§§constant(9));
         §§push(§§constant(10));
         §§push(true);
         if(getTimer() + 1)
         {
            break loop3;
         }
         §§pop() implements ;
      }
      while(ord("\b"));
      addr653fa:
   }
   setProperty(§§pop(), _X, §§pop());
   addr65535:
}
