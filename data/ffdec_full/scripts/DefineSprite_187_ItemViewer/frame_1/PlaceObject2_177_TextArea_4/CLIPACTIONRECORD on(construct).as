on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(true and true))
         {
            if(!(true and true))
            {
               while(true)
               {
                  set(",","{invalid_utf8=169}f");
                  set("{invalid_utf8=190}",0);
                  set("\x1d{invalid_utf8=150}\x04",true);
                  set("\b\x06\b\x07\x1d{invalid_utf8=150}\x07",false);
                  §§push("\b\b\x01");
                  §§push("");
                  if(!(getTimer() + 1))
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addr25706);
                  }
                  §§goto(addr257d2);
                  break loop3;
               }
               §§goto(addr257d1);
               addr256d4:
            }
         }
         else
         {
            §§push(false);
         }
         if(§§pop())
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addr256d4);
   }
   if(getTimer())
   {
      while(true)
      {
         set("{invalid_utf8=150}\x02",false);
         set("\x05",false);
         set("\x12{invalid_utf8=157}\x02",false);
         y = true;
         set("{invalid_utf8=136}\t",true);
         §§push("\x03");
         §§push(-1);
         if(getTimer() + 1)
         {
            break loop3;
         }
         §§pop() implements ;
         §§goto(addr25740);
         addr25740:
      }
      break loop3;
      addr25706:
   }
   addr257d1:
   §§pop() implements ;
   addr257d2:
   set(§§pop(),§§pop());
   styleSheet = "";
   text = "";
   url = "";
   wordWrap = false;
}
