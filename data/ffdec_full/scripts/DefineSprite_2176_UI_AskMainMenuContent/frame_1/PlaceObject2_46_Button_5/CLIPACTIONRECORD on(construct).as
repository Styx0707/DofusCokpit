on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(false)
         {
            if(!ord("\x03"))
            {
               §§goto(addr2dba5);
            }
         }
         else
         {
            §§push(55884582);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      set(§§constant(11),false);
      §§goto(addr2dc6a);
   }
   while(true)
   {
      set("{invalid_utf8=150}\x05","\x07&{invalid_utf8=187}T\x03{invalid_utf8=157}\x02");
      S = "{invalid_utf8=136}\b";
      set("\x02",true);
      set("(8","@`");
      set("\x1d{invalid_utf8=150}\x04","@`");
      set("\b\x0b\x05",false);
      §§push("\x1d");
      §§push("{invalid_utf8=150}\x04");
      if(getTimer())
      {
         break loop2;
      }
      §§pop() implements ;
      §§goto(addr2dbe3);
      addr2dbe3:
   }
   addr2dc6a:
   return;
   addr2dba5:
   setProperty(§§pop(), _X, §§pop());
   §§goto(addr2dc6a);
}
