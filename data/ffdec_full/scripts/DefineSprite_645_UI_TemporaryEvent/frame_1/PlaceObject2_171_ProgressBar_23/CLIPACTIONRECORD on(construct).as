on(construct){
   loop1:
   while(true)
   {
      while(true)
      {
         if(!(true or true))
         {
            if(!ord("\x02"))
            {
               §§goto(addr1802b);
            }
         }
         else
         {
            §§push(145944050);
         }
         if(!§§pop())
         {
            break;
         }
         break loop1;
      }
      set(§§pop(),§§pop());
      §§goto(addr1810a);
   }
   addr1809a:
   disableBackground = true;
   enabled = false;
   set("\x18\x19\x18",100);
   set("\x18\x1d\t",0);
   §§push("\x1a\r\f");
   §§push("ProgressBarDefaultRenderer");
   if(getTimer() + 1)
   {
      set(§§pop(),§§pop());
      §§push("showAnimOnLoad");
      §§push(false);
      while(true)
      {
         set(§§pop(),§§pop());
         showGradient = false;
         styleName = "default";
         uberMaximum = 100;
         uberMinimum = 0;
         §§push("value");
         §§push(0);
         if(getTimer())
         {
            break loop2;
         }
         §§pop() implements ;
         §§goto(addr1809a);
         set(§§pop(),§§pop());
         §§push("showAnimOnLoad");
         §§push(false);
      }
      break loop2;
      addr1802b:
   }
   addr1810a:
   §§pop()();
}
