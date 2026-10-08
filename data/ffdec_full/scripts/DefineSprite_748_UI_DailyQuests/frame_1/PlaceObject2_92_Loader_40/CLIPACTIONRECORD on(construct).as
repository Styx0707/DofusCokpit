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
         §§push(false);
      }
      if(!§§pop())
      {
         autoLoad = true;
         centerContent = false;
         contentPath = "QuestionMark";
         enabled = true;
         fallbackContentPath = "";
         §§push("forceReload");
         §§push(false);
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr199ba);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   scaleContent = true;
   styleName = "default";
   addr199ba:
}
