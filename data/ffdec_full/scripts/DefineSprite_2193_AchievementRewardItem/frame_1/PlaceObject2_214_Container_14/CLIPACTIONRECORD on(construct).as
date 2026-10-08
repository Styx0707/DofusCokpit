on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         while(true)
         {
            if(!ord("\x0b"))
            {
               if(!(0x32D2B9B4 & 0x32D2B9B4))
               {
                  break;
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
            if(!getTimer())
            {
               §§push(new §\§\§pop()§());
               return;
            }
            break loop1;
         }
         §§goto(addr12f0c);
      }
      return;
   }
   set("{invalid_utf8=150}\x03","");
   set("\b","2{invalid_utf8=157}\x02");
   s = false;
   set("{invalid_utf8=136}\n",false);
   §§push("\x03");
   §§push(false);
   if(getTimer())
   {
      while(true)
      {
         set(§§pop(),§§pop());
         set("{invalid_utf8=191}y","2{invalid_utf8=157}\x02");
         set("{invalid_utf8=199}",0);
         set("{invalid_utf8=146}{invalid_utf8=191}",2);
         set("\x1d{invalid_utf8=150}\x04",true);
         §§push("\b\x07\b\x03\x1d{invalid_utf8=150}\x07");
         §§push("\b\b\x01");
         if(!(getTimer() + 1))
         {
            §§goto(addr12f42);
            §§push(getProperty(§§pop(), _X));
         }
         addr12f70:
         set(§§pop(),§§pop());
         return;
         addr12f42:
      }
      return;
      addr12f0c:
   }
   startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
   §§goto(addr12f70);
}
