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
                  set("{invalid_utf8=194}p",false);
                  set("5",false);
                  set("\x1d{invalid_utf8=150}\x04","\b\x06\x05");
                  §§push("\x1d{invalid_utf8=150}\x04");
                  §§push(false);
                  if(!ord("\x03"))
                  {
                     §§goto(addr46071);
                     §§push(new §\§\§pop()§());
                  }
                  §§goto(addr46125);
                  break loop3;
               }
               §§goto(addr46124);
               addr46045:
            }
         }
         else
         {
            §§push(214242360);
         }
         if(!§§pop())
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr46045);
   }
   if(getTimer())
   {
      while(true)
      {
         set("{invalid_utf8=150}\x05",true);
         set("\x078\x14{invalid_utf8=197}\f{invalid_utf8=157}\x02",false);
         m = "{invalid_utf8=136}\t";
         set("\x03",true);
         §§push("{");
         §§push("{invalid_utf8=136}\t");
         if(ord("\x04"))
         {
            break loop3;
         }
         §§pop() implements ;
         §§goto(addr460a5);
         addr460a5:
      }
      break loop3;
      addr46071:
   }
   addr46124:
   startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
   addr46125:
   set(§§pop(),§§pop());
}
