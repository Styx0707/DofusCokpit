on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!ord("\x03"))
         {
            if(!(0x35CFF0D4 | 0x35CFF0D4))
            {
               break;
            }
         }
         else
         {
            §§push("\x07");
         }
         if(!ord(§§pop()))
         {
            break;
         }
         break loop1;
      }
      while(true)
      {
         set("{invalid_utf8=150}\x03","");
         set("\x07","2{invalid_utf8=157}\x02");
         q = false;
         set("{invalid_utf8=136}\x05",false);
         §§push("\x01");
         §§push(false);
         if(!getTimer())
         {
            §§pop()[§§pop()] = §§pop();
         }
         else
         {
            set(§§pop(),§§pop());
            set(§§constant(7),§§constant(3));
            set(§§constant(8),0);
            set(§§constant(9),2);
            set(§§constant(10),false);
            §§push(§§constant(11));
            §§push(§§constant(3));
            if(false)
            {
               §§pop()[§§pop()] = §§pop();
               break loop1;
            }
         }
         set(§§pop(),§§pop());
         break;
      }
      §§goto(addr22aba);
   }
   if(ord("\x0b"))
   {
      break loop2;
   }
   addr22aba:
   getProperty(§§pop(), _X);
}
