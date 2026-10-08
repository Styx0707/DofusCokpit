on(construct){
   loop1:
   while(true)
   {
      if(false)
      {
         if(!(0x3A1DC56F | 0x3A1DC56F))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 and _temp_1))
      {
         break;
      }
      addr1f0c:
      while(true)
      {
         disableBackground = false;
         enabled = true;
         set("\x18\x19\x18",100);
         set("\x18\x1d\t",0);
         §§push("\x1a\r\f");
         §§push("ProgressBarDefaultRenderer");
         if(!getTimer())
         {
            setProperty(§§pop(), _X, §§pop());
            break;
         }
         set(§§pop(),§§pop());
         showAnimOnLoad = false;
         showGradient = false;
         styleName = "BrownProgressBarGain";
         uberMaximum = 100;
         §§push("uberMinimum");
         §§push(0);
         break loop1;
         setProperty(§§pop(), _X, §§pop());
      }
      return;
   }
   set(§§pop(),§§pop());
   value = 0;
   §§goto(addr1f0c);
}
