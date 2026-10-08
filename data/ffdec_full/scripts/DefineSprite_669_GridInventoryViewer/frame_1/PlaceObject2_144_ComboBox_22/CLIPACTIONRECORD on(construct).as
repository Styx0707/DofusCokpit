on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         while(true)
         {
            if(!(true or true))
            {
               if(!(true and true))
               {
                  §§goto(addr11159);
               }
            }
            else
            {
               §§push(228913703);
            }
            if(!§§pop())
            {
               break;
            }
            if(false)
            {
               break loop3;
            }
            break loop2;
         }
         §§goto(addr1114e);
      }
      var §§pop() = §§pop();
      §§goto(addr11314);
   }
   set("{invalid_utf8=150}\x05","\x07\'{invalid_utf8=242}{invalid_utf8=164}\r{invalid_utf8=157}\x02");
   set("{invalid_utf8=206}","{invalid_utf8=136}\t");
   set("\x03","{invalid_utf8=136}\t");
   U = "\x0fU";
   set("{invalid_utf8=157}",20);
   set("\x1d{invalid_utf8=150}\x07","\b\x10\x07\x04");
   §§push("");
   §§push(true);
   if(getTimer())
   {
      loop1:
      while(true)
      {
         set(§§pop(),§§pop());
         set("",false);
         set("\x1d{invalid_utf8=150}\x07",0);
         set("\b\x11\x07\x04",4);
         set("",0);
         §§push("");
         §§push(0);
         if(!getTimer())
         {
            §§pop()[§§pop()] = §§pop();
            §§goto(addr111c5);
         }
         else
         {
            set(§§pop(),§§pop());
            §§push(§§constant(16));
            §§push(4);
            while(true)
            {
               set(§§pop(),§§pop());
               set("\b\x12\b\x13\x1d{invalid_utf8=150}\x07",4);
               set("\b\x14\x07\n","");
               set("",10);
               §§push("\x1d{invalid_utf8=150}\x07");
               §§push(20);
               if(!(getTimer() + 1))
               {
                  startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
                  continue loop1;
               }
               set(§§pop(),§§pop());
               §§push(§§constant(16));
               §§push(4);
            }
            addr11205:
            §§pop() extends §§pop();
            addr11159:
         }
         set(§§pop(),§§pop());
         set("\b\x15\x07\x14","");
         addr11314:
         return;
         addr111c5:
      }
      break loop3;
   }
   §§goto(addr11205);
}
