on(construct){
   while(true)
   {
      if(!ord("\x03"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\b");
      }
      if(ord(§§pop()))
      {
         autoLoad = true;
         centerContent = false;
         contentPath = "TurquoiseDofus";
         enabled = false;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         if(!getTimer())
         {
            §§pop() implements ;
            §§goto(addr107a3);
         }
      }
      set(§§pop(),§§pop());
      §§push("scaleContent");
      §§push(true);
      break;
   }
   set(§§pop(),§§pop());
   styleName = "none";
   addr107a3:
}
