on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!(0x1E090439 | 0x1E090439))
         {
            if(!(0x1E090439 & 0x1E090439))
            {
               §§goto(addr195dd);
            }
         }
         else
         {
            §§push(731065599);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      set(§§constant(11),false);
      §§goto(addr196a2);
   }
   if(getTimer() + 1)
   {
      while(true)
      {
         set("{invalid_utf8=150}\x05","\x07{invalid_utf8=255},{invalid_utf8=147}+{invalid_utf8=157}\x02");
         R = "{invalid_utf8=136}\x07";
         set("\x02",true);
         set("{invalid_utf8=136}{invalid_utf8=201}","s");
         set("\x1d{invalid_utf8=150}\x04","s");
         set("\b\x0b\x05",false);
         §§push("\x1d");
         §§push("{invalid_utf8=150}\x04");
         if(getTimer())
         {
            break loop2;
         }
         startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
         §§goto(addr1961b);
         addr1961b:
      }
      addr196a2:
      return;
      addr195dd:
   }
   startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
   §§goto(addr196a2);
}
