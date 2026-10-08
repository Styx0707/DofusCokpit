on(construct){
   while(true)
   {
      if(!(true or true))
      {
         if(!(true and true))
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      disableBackground = false;
      enabled = true;
      set("\x18\x19\x18",10000);
      set("\x18\x1d\t",0);
      set("\x1a\r\f","ProgressBarDefaultRenderer");
      showAnimOnLoad = false;
      §§push("showGradient");
      §§push(false);
      if(!ord("\x0b"))
      {
         §§goto(addr155fa);
      }
      break;
   }
   set(§§pop(),§§pop());
   styleName = "BrownProgressBar";
   uberMaximum = 100;
   uberMinimum = 0;
   value = 0;
   addr155fa:
   new §\§\§pop()§();
}
