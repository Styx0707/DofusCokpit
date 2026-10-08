on(construct){
   while(true)
   {
      if(!(0x29588DF7 | 0x29588DF7))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
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
            §§goto(addr7c31);
         }
      }
      set(§§pop(),§§pop());
      §§push("styleName");
      §§push("TtgProgressBar");
      break;
   }
   set(§§pop(),§§pop());
   uberMaximum = 100;
   uberMinimum = 0;
   value = 0;
   addr7c31:
   new §\§\§pop()§();
}
