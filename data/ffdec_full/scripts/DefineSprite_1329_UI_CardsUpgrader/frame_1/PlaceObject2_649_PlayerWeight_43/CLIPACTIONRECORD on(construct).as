on(construct){
   while(true)
   {
      if(!ord("\b"))
      {
         if(!(0x15794A1E | 0x15794A1E))
         {
            break;
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
      disableBackground = false;
      enabled = true;
      set("\x18\x19\x18",100);
      set("\x18\x1d\t",0);
      set("\x1a\r\f","ProgressBarDefaultRenderer");
      showAnimOnLoad = false;
      §§push("showGradient");
      §§push(false);
      if(!(getTimer() + 1))
      {
         §§push(§§pop()());
      }
      set(§§pop(),§§pop());
      styleName = "BrownProgressBar";
      uberMaximum = 100;
      uberMinimum = 0;
      §§push("value");
      §§push(0);
      if(!ord("\x0b"))
      {
         setProperty(§§pop(), _X, §§pop());
      }
      else
      {
         addr13c39:
         set(§§pop(),§§pop());
      }
      return;
   }
   §§goto(addr13c39);
}
