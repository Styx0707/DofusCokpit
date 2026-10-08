on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!ord("\x0b"))
         {
            if(false)
            {
               while(true)
               {
                  set("\b\b\x01",0);
                  set("",true);
                  set("",false);
                  set("","\x1d{invalid_utf8=150}\x04");
                  §§push("\b\t\x05\x01\x1d{invalid_utf8=150}\x04");
                  §§push("\b\n\x05");
                  if(false)
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addr108c7);
                  }
                  §§goto(addr10995);
                  break loop3;
               }
               §§goto(addr10994);
               addr10891:
            }
         }
         else
         {
            §§push(77926841);
         }
         if(!(§§pop() - 1))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      set(§§constant(6),§§constant(7));
      §§goto(addr10891);
   }
   if(ord("\x05"))
   {
      while(true)
      {
         set("{invalid_utf8=150}\x05",false);
         set("\x07{invalid_utf8=185}\x11{invalid_utf8=165}\x04Q{invalid_utf8=157}\x02",false);
         set("{invalid_utf8=128}",false);
         set("{invalid_utf8=136}\x04",true);
         set("\x01",true);
         §§push("{invalid_utf8=174}");
         §§push(-1);
         if(getTimer() + 1)
         {
            break loop3;
         }
         setProperty(§§pop(), _X, §§pop());
         §§goto(addr10901);
         addr10901:
      }
      break loop3;
      addr108c7:
   }
   addr10994:
   §§pop() extends §§pop();
   addr10995:
   set(§§pop(),§§pop());
   text = "";
   url = "";
   wordWrap = true;
}
