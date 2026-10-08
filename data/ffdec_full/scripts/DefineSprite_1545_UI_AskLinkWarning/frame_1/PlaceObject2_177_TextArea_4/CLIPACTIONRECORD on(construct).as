on(construct){
   loop2:
   while(true)
   {
      loop3:
      while(true)
      {
         if(!(0x02F022D0 & 0x02F022D0))
         {
            if(false)
            {
               while(true)
               {
                  set("\x1d{invalid_utf8=150}\x04","\b\x06\b\x07\x1d{invalid_utf8=150}\x07");
                  set("\b\b\x01",0);
                  set("",true);
                  §§push("");
                  §§push(false);
                  if(!(getTimer() + 1))
                  {
                     setProperty(§§pop(), _X, §§pop());
                     §§goto(addrf494);
                  }
                  §§goto(addrf4d1);
                  break loop3;
               }
               §§goto(addrf591);
               addrf46a:
            }
         }
         else
         {
            §§push(681228419);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 & _temp_1))
         {
            break;
         }
         break loop2;
      }
      set(§§pop(),§§pop());
      §§goto(addrf46a);
   }
   do
   {
      set("{invalid_utf8=150}\x05",false);
      set("\x07{invalid_utf8=131}{invalid_utf8=184}{invalid_utf8=154}(L`{invalid_utf8=157}\x02",false);
      set("{invalid_utf8=160}",false);
      set("{invalid_utf8=136}\x05",true);
      set("\x01",true);
      §§push("{invalid_utf8=182}p");
      §§push(-1);
      break loop3;
      var §§pop() = §§pop();
      set(§§pop(),§§pop());
      set("","\x1d{invalid_utf8=150}\x04");
      set("\b\t\x05\x01\x1d{invalid_utf8=150}\x04","\b\n\x05");
      set("4P{invalid_utf8=157}\x02","\b\n\x05");
      set(">","\b\n\x05");
      §§push("#{invalid_utf8=150}\x04");
      §§push(true);
      if(!(getTimer() + 1))
      {
         var §§pop() = §§pop();
      }
      else
      {
         §§goto(addrf592);
      }
   }
   while(true);
   addrf494:
   addrf591:
   addrf592:
   set(§§pop(),§§pop());
}
