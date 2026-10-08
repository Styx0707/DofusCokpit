on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(false)
         {
            if(!ord("\x07"))
            {
               §§goto(addr4c2e);
            }
         }
         else
         {
            §§push(248391910);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      set(§§constant(11),true);
      §§goto(addr4cf8);
   }
   if(getTimer() + 1)
   {
      while(true)
      {
         set("{invalid_utf8=150}\x05","\x07{invalid_utf8=230}({invalid_utf8=206}\x0e{invalid_utf8=157}\x02");
         X = "{invalid_utf8=136}\x07";
         set("\x02",true);
         set("\f","{invalid_utf8=181}");
         set("\x1d{invalid_utf8=150}\x04","{invalid_utf8=181}");
         set("\b\x0b\x05\x01\x1d",false);
         §§push("{invalid_utf8=150}\x04");
         §§push("\b");
         if(ord("\x07"))
         {
            break loop2;
         }
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr4c72);
         addr4c72:
      }
      addr4cf8:
      return;
      addr4c2e:
   }
   §§goto(addr4cf8);
}
