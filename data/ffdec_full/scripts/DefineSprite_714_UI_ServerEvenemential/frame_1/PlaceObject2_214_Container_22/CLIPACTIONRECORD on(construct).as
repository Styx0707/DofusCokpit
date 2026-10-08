on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!(true and true))
         {
            if(!(0x0284963A | 0x0284963A))
            {
               §§goto(addr1b714);
            }
         }
         else
         {
            §§push(819564294);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr1b7fe);
   }
   if(getTimer())
   {
      §§push("\x179");
      §§push("J{invalid_utf8=150}");
      while(true)
      {
         set(§§pop(),§§pop());
         set(";","{invalid_utf8=136}\b");
         set("\x02",false);
         set("\x179",true);
         §§push("J{invalid_utf8=150}");
         §§push(false);
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr1b73b);
         }
         addr1b7c8:
         set(§§pop(),§§pop());
         highlightRenderer = "";
         id = 1;
         margin = 0;
         set("\x1a\x1e\b",false);
         §§push("styleName");
         §§push("default");
         if(!(getTimer() + 1))
         {
            addr1b7fe:
            getProperty(§§pop(), _X);
            return;
         }
         break loop2;
         addr1b73b:
      }
      addr1b714:
   }
   duplicateMovieClip(§§pop(),§§pop(),§§pop());
   §§goto(addr1b7c8);
}
